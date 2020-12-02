#! /usr/bin/python3

# the runner recipe from https://docs.scrapy.org/en/latest/topics/practices.html
from sys import argv
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
	for name in ["MONGODB_URI", "MONGODB_DB", "WORDS_COLLECTION", "TRANSLATION_COLLECTION", "TOPIC"]:
		if name not in settings:
			print(f"{name} not found in settings")
			exit()

	client = pymongo.MongoClient(settings["MONGODB_URI"])
	db = client[settings["MONGODB_DB"]]

	# does the collection of basic words seem to be filled?
	collection = f"{settings['WORDS_COLLECTION']}_basic"
	number_of_basic_words = db[collection].count_documents({})  # returns 0 for nonexisting base
	basic_vocab_needed = number_of_basic_words < 1000  # let's say this is enough

	# do we have translation for the topic
	collection = settings['TRANSLATION_COLLECTION']
	topic_english = settings["TOPIC"].lower().replace("_", " ")
	number_of_translations = db[collection].count_documents({"english": topic_english})
	translation_needed = number_of_translations < 1

	client.close()

	return [basic_vocab_needed, translation_needed]


# callback function for the case when we need to exit early
def spider_closing(spider, **kwargs):
	# log.msg("Early shutdown", level=log.INFO)
	print("CrawlerRunner: Early shutdown.")
	reactor.stop()


def spider_warning(spider, **kwargs):
	print("CrawlerRunner: moving on.")


@defer.inlineCallbacks
def crawl(runner, basic_vocab_needed, translation_needed):

	if basic_vocab_needed:
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

	# The basic words are from a site that is supposed
	# to be surefire relevant to the topic -  we are currently using Wikipedia.
	# This may fail if, for example, Wikipedia does not have a page on our topic.
	# However, we can move on without that word set.
	crawler = runner.create_crawler(TopicVocabSpider)
	crawler.signals.connect(spider_warning, signal=signals.spider_closed)
	yield crawler.crawl()

	# Extended vocab is more of a fishing expedition, so it can fail.
	# Our vocab will be somewhat smaller in that case.
	crawler = runner.create_crawler(ExtendedTopicVocabSpider)
	crawler.signals.connect(spider_warning, signal=signals.spider_closed)
	yield crawler.crawl()
	reactor.stop()


def report(settings):
	client = pymongo.MongoClient(settings["MONGODB_URI"])
	db = client[settings["MONGODB_DB"]]

	# does the collection of basic words seem to be filled?
	collection = f"{settings['WORDS_COLLECTION']}_{settings['TOPIC']}"
	for line in db[collection].find({'count': {'$gt': 10}}).sort("count", -1):
		print("\t".join([str(v) for v in line.values()]))


def main():
	if len(argv) > 1:
		topic = argv[1].lower()
	else:
		topic = "genome"
		print(usage_statement.format(topic=topic, cmd=argv[0]))
	print(f"The topic today is {topic}.")

	settings = get_project_settings()
	settings.set("TOPIC", topic)

	# do we need basic vocab, do we need topic translation?
	[basic_vocab_needed, translation_needed] = prerequisites(settings)
	print(f"Do we need basic vocab? {basic_vocab_needed}.")
	print(f"Do we need topic translation? {translation_needed}.")

	runner = CrawlerRunner(settings)

	crawl(runner, basic_vocab_needed, translation_needed)
	reactor.run()  # the script will block here until the last crawl call is finished

	report(settings)


if __name__ == "__main__":
	main()