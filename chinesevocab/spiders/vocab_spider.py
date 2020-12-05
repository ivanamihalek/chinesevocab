import re

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


from urllib.parse import unquote

from scrapy import Spider, signals
from scrapy.exceptions import CloseSpider
from pymongo import MongoClient

from chinesevocab.items import ChineseTextItem


# this class is incomplete - would be abstract in some other language
# TranslationSpider, TopicVocabSpider, and ExtendedTopicVocabSpider inherit from here
# and implement the abstract methods
class VocabSpider(Spider):
	# TODO skip website we scraped

	# The settings attribute is set in the base Spider class after the spider is initialized.
	# If you want to use the settings before the initialization (e.g., in your spider’s __init__() method),
	# you’ll need to override the from_crawler() method.
	# https://docs.scrapy.org/en/latest/topics/settings.html#how-to-access-settings
	def __init__(self, crawler, **kwargs):
		super().__init__(**kwargs)
		# if I don't store the crawler reference here, I get errors like
		#   File "/usr/local/lib/python3.8/dist-packages/scrapy/spidermiddlewares/httperror.py",
		#   line 49, in process_spider_exception
		#   spider.crawler.stats.inc_value('httperror/response_ignored_count')
		#   AttributeError: 'ExtendedTopicVocabSpider' object has no attribute 'crawler'
		self.crawler = crawler
		mongo_uri = crawler.settings['MONGODB_URI']
		mongo_db  = crawler.settings['MONGODB_DB']
		self.client = MongoClient(mongo_uri)
		self.db = self.client[mongo_db]
		self.collection = crawler.settings['TRANSLATION_COLLECTION']
		# if we ran from command line, the topic should be set here
		# (unless the user omitted to do so), however:
		if getattr(self, "topic", None) is None:
			# the topic will be in the settings dict  if we run the whole shebang from CrawlerRunner
			self.topic = crawler.settings.get("TOPIC", None)  # I will have to check if it is set

	@classmethod
	def from_crawler(cls, crawler,  *args, **kwargs):
		# the command line args are in kwargs
		# need to pass them otherwise I lose them as I inherit
		return cls(crawler, **kwargs)

	def _package_chinese_item(self, unquoted_url, jumbo_string):
		topic = getattr(self, 'topic', None)
		item = ChineseTextItem()
		item['collection'] = f"words_{topic}"
		item['url'] = unquoted_url
		item['text'] = jumbo_string
		return item

	def _extract_chinese_content(self, response):
		unquoted_url = unquote(unquote(response.url))
		response_chunks = response.css('*::text').getall()
		if not response_chunks: return
		# how much of that is actually chinese?
		cc_pattern = r"[\u4e00-\u9FFF]"  # chinese characters
		space_pattern = r"[\n\t]+|\[\d+\]"
		usable_chunks = []
		for chunk in response_chunks:
			# get rid of spaces and reference numbers
			spaced_out_chunk = re.sub(space_pattern, "", chunk)
			if len(spaced_out_chunk) == 0: continue
			number_of_chinese_characters = len(re.findall(cc_pattern, spaced_out_chunk))
			if number_of_chinese_characters/len(spaced_out_chunk) < .8: continue
			usable_chunks.append(spaced_out_chunk)
		return self._package_chinese_item(unquoted_url, "".join(usable_chunks))

	def _topic_translation(self):
		# the second argument is projection, it specifies which arguments to return (1=return, 0=do not)
		ret = self.db[self.collection].find_one({'english': {'$eq': self.topic.replace("_", " ")}}, {'chinese': 1})
		return None if (not ret or 'chinese' not in ret or not ret['chinese']) else ret['chinese']

	def _store_translation(self, item):
		mongo_filter = {'chinese': item['chinese']}
		mongo_update = {'$set': dict(item)}
		self.db[self.collection].find_one_and_update(mongo_filter, mongo_update, upsert=True)

	def close(self, **kwargs):
		self.client.close()

	# needs override
	def parse(self, response, **kwargs):
		pass
