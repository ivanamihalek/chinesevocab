#! /usr/bin/python3

#    Chinesevocab collects several hundred non-generic words related to a specified topic
#
#    Copyright (C) 2020 Ivana Mihalek
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
#    Contact: ivana.mihalek@gmail.com

# Run with
# ./run.py <topic>
#
# The topic can be something like "genome" or "fashion."
# If the topic consist of two or three words you can link them with underscore,
# for example "The_Internet", or "elementary_particle," but keep in mind that this
# compound term should be discoverable in a dictionary for the pipeline to run as planned.
#
#
# ./run.py runs all spiders in this app in the order in
# which they are supposed to be run:
# 1. Fill the database collection of generic words (to be able to eliminate them later)
#    (this will be run only once - if the collection exists, we skip the step)
# 2. Translate the topic from English to Chinese - if the translation already
#    exists in the translation collection, we skip the step
# 3. Start the collection of the words on the specified topic by scraping
#    the Chinese Wikipedia page
# 4. Look for some more words and the word usage frequency by following the first
#    couple of tens of links from a search engine.


from sys import argv

from pymongo import MongoClient, UpdateOne
from pymongo.errors import BulkWriteError
from twisted.internet import reactor, defer
from scrapy.crawler import CrawlerRunner
from scrapy.utils.project import get_project_settings
from scrapy import signals

import pymongo

from chinesevocab.spiders.generic_vocab_spider import GenericVocabSpider
from chinesevocab.spiders.extended_topic_vocab_spider import ExtendedTopicVocabSpider
from chinesevocab.spiders.topic_vocab_spider import TopicVocabSpider
from chinesevocab.spiders.translation_spider import TranslationSpider

usage_statement = '''
Using '{topic}' as default topic.
You can change the topic by running: {cmd} <topic>.
'''


def prerequisites(settings):
	""" Check whether we haev evrything defined, and if we can skip some steps."""
	for name in ["MONGODB_URI", "MONGODB_DB", "TEXT_COLLECTION", "WORDS_COLLECTION", "TRANSLATION_COLLECTION", "TOPIC"]:
		if name not in settings:
			print(f"{name} not found in settings")
			exit()

	client = MongoClient(settings["MONGODB_URI"])
	db = client[settings["MONGODB_DB"]]

	# does the collection of generic words seem to be filled?
	collection = f"{settings['WORDS_COLLECTION']}_generic"
	number_of_generic_words = db[collection].count_documents({})  # returns 0 for nonexisting base
	generic_vocab_needed = number_of_generic_words < 1000  # let's say this is enough

	# do we have translation for the topic
	collection = settings['TRANSLATION_COLLECTION']
	topic_english = settings["TOPIC"].lower().replace("_", " ")
	number_of_translations = db[collection].count_documents({"english": topic_english})
	translation_needed = number_of_translations < 1

	client.close()

	return [generic_vocab_needed, translation_needed]


def patches(settings):
	""" Some as hoc patches, until a better solution is found."""
	# some patches, until a better solution is found
	client = pymongo.MongoClient(settings["MONGODB_URI"])
	db = client[settings["MONGODB_DB"]]
	collection = f"{settings['WORDS_COLLECTION']}_generic"
	# For some reason, the generic word lists that I am aware of, do not include
	# some very common  words such as "one", "first", "some", "this kind", and even "not."
	# We want to exclude these words from topic-special lists.
	patch_words = ["一个", "这种", "一种", "这个", "不是", "第一", "时", "英语"]
	requests = []
	for word in patch_words:
		requests.append(UpdateOne({'_id': word}, {"$inc": {"count": 1}}, upsert=True))
	try:
		db[collection].bulk_write(requests, ordered=False)
	except BulkWriteError as bwe:
		print(bwe.details)

	client.close()


def spider_closing(spider, **kwargs):
	""" Callback function for the cases when we need to exit early. """
	# finished is ok
	# log.msg("Early shutdown", level=log.INFO)
	if kwargs and "reason" in kwargs and kwargs['reason'] != "finished":
		print("CrawlerRunner: Early shutdown.")
		print("The reason quoted:", kwargs['reason'])
		reactor.stop()
	# otherwise we do not care

def spider_warning(spider, **kwargs):
	""" There was warning, but we are moving on. """
	if kwargs and "reason":
		print("Warning:", kwargs['reason'])
		print("CrawlerRunner: moving on.")


@defer.inlineCallbacks
def crawl(runner, generic_vocab_needed, translation_needed):
	""" The core of the operation: calling spiders sequentially."""
	# The runner recipe from https://docs.scrapy.org/en/latest/topics/practices.html
	if generic_vocab_needed:
		# if this spider breaks down we can still limp along
		# though the results may be skewed toward generic words, irrelevant to the topic
		crawler = runner.create_crawler(GenericVocabSpider)
		crawler.signals.connect(spider_warning, signal=signals.spider_closed)
		yield crawler.crawl()

	if translation_needed:
		#  we cannot proceed if we do not know what is Chinese word for our topic
		crawler = runner.create_crawler(TranslationSpider)
		crawler.signals.connect(spider_closing, signal=signals.spider_closed)
		yield crawler.crawl()

	# The generic words are from a site that is supposed
	# to be surefire relevant to the topic -  we are currently using Wikipedia.
	# This may fail if, for example, Wikipedia does not have a page on our topic.
	# However, we can move on without that word set.
	crawler = runner.create_crawler(TopicVocabSpider)
	crawler.signals.connect(spider_warning, signal=signals.spider_closed)
	yield crawler.crawl()

	# # Extended vocab is more of a fishing expedition, so it can fail.
	# # Our vocab will be somewhat smaller in that case.
	crawler = runner.create_crawler(ExtendedTopicVocabSpider)
	crawler.signals.connect(spider_warning, signal=signals.spider_closed)
	yield crawler.crawl()
	reactor.stop()


def report(settings, topic):
	""" Output the words and their frequency. """
	client = pymongo.MongoClient(settings["MONGODB_URI"])
	db = client[settings["MONGODB_DB"]]

	# does the collection of generic words seem to be filled?
	collection = f"{settings['WORDS_COLLECTION']}_{settings['TOPIC']}"
	words_found = list(db[collection].find({'count': {'$gt': 20}}).sort("count", -1))
	if len(words_found) > 0:
		with open(f"{topic}.tsv", "w") as outf:
			print("\t".join(["word", "frequency"]),file=outf)
			for line in words_found:
				print("\t".join([str(v) for v in line.values()]),file=outf)


def main():
	if len(argv) > 1:
		topic = argv[1].lower()
	else:
		topic = "genome"
		print(usage_statement.format(topic=topic, cmd=argv[0]))
	print(f"The topic today is {topic}.")

	settings = get_project_settings()
	settings.set("TOPIC", topic)

	# do we need generic vocab, do we need topic translation?
	[generic_vocab_needed, translation_needed] = prerequisites(settings)
	print(f"Do we need generic vocab? {generic_vocab_needed}.")
	print(f"Do we need topic translation? {translation_needed}.")
	# some patches, until a better solution is found
	patches(settings)

	runner = CrawlerRunner(settings)

	crawl(runner, generic_vocab_needed, translation_needed)
	reactor.run()  # the script will block here until the last crawl call is finished

	report(settings, topic)


if __name__ == "__main__":
	main()