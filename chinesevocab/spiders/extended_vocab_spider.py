
# You can provide command line arguments to your spiders by using the -a option when running them:
# scrapy crawl extended -a topic=genome
# These arguments are passed to the Spider’s __init__ method and become spider attributes by default.
# Suggested use scrapy crawl plain -O plain.json -a topic=genome 2>&1 | grep DEBUG > debug.log
from pprint import pprint

import pymongo
import scrapy
from scrapy.exceptions import CloseSpider
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor

from chinesevocab.items import ChineseTextItem
from urllib.parse import unquote, urlparse

from chinesevocab.pipeline.mongo_text_component import MongoTextComponent
from chinesevocab.pipeline.text_parser_component import TextParserComponent
from chinesevocab.pipeline.mongo_words_component import MongoWordsComponent


class ExtendedVocabSpider(scrapy.Spider):
	# for the purposes of this demo, the extended search consists
	# of the first three pages returned by google
	name = "extended"
	# note  custom_settings has to be defined as a class (not an instance) attribute
	# custom_settings = {'ITEM_PIPELINES': {
	# 	MongoTextComponent:  100,
	# 	TextParserComponent: 200,
	# 	MongoWordsComponent: 300},
	# 	'ROBOTSTXT_OBEY': False  # let's just ask for a page or two
	# }
	custom_settings = {'ROBOTSTXT_OBEY': False}  # let's just ask for a page or two
	domains_not_allowed = ['upload.wikimedia.org', 'hr.wikipedia.org', 'accounts.google.com']

	link_extractor = LinkExtractor()

	def _get_topic(self):
		topic = getattr(self, 'topic', None)
		if not topic:
			topic = "genome"
			setattr(self,  'topic', topic)
		return topic

	def _topic_translation(self):
		topic = getattr(self, 'topic', None)
		# we should have the translation at this point
		client     = pymongo.MongoClient(self.settings['MONGODB_URI'])
		db         = client[self.settings['MONGODB_DB']]
		collection = self.settings['TRANSLATION_COLLECTION']
		# the second argument is projection, it specifies which arguments to return (1=return, 0=do not)
		ret = db[collection].find_one({'english': {'$eq': topic}}, {'chinese': 1})
		if not ret or 'chinese' not in ret or not ret['chinese']:
			raise CloseSpider(f"Chinese translation for the topic '{topic}' not found in the local DB")
		client.close()
		return ret['chinese']

	def start_requests(self):  # must return an iterable of Requests
		topic_chinese = self._topic_translation()
		raw_pages_domain = "https://google.com"
		path = f"search?q={topic_chinese}"
		urls = [f"{raw_pages_domain}/{path}&start{i*10}" for i in range(3)]

		for url in urls:
			yield scrapy.Request(url=url, callback=self.parse)

	def _strip_link(self, compound_link):
		compound_pieces = compound_link.split("=")
		if len(compound_pieces)<2: return None
		if compound_pieces[1][:4] != "http": return None
		url = compound_pieces[1].split("&")[0]
		parsed_url = urlparse(url)
		if parsed_url.netloc in self.domains_not_allowed: return None
		if parsed_url.path.split(".")[-1] in ["image", "png", "jpg", "gif"]: return None
		return url

	def parse(self, response, **kwargs):
		topic = self._get_topic()
		collection = f"words_{topic}"  # the collection we will be storing this into
		# this is working in python3 shell and for response.url
		# unquoted_url = unquote(response.url)  # back from percentage encoding to utf
		for link in self.link_extractor.extract_links(response):
			# google is going back to its whatever wih the link
			# I just need the link
			# nice of them to keep the link unmangled
			url = self._strip_link(link.url)
			if not url: continue
			print(url)
