
# You can provide command line arguments to your spiders by using the -a option when running them:
# scrapy crawl topic -a topic=genome
# These arguments are passed to the Spider’s __init__ method and become spider attributes by default.
# Suggested use scrapy crawl plain -O plain.json -a topic=genome 2>&1 | grep DEBUG > debug.log

import scrapy

from chinesevocab.items import ChineseTextItem
from urllib.parse import unquote
from re import sub

from chinesevocab.pipeline.mongo_text_component import MongoTextComponent
from chinesevocab.pipeline.text_parser_component import TextParserComponent
from chinesevocab.pipeline.mongo_words_component import MongoWordsComponent
from chinesevocab.pipeline.component_utils import *


class TopicVocabSpider(scrapy.Spider):

	# name must be unique within a project
	# => note this is how we invoke it from the scrapy crawl command
	name = "topic"
	start_netloc = "zh.wikipedia.org"
	# note  custom_settings has to be defined as a class (not an instance) attribute
	custom_settings = {'ITEM_PIPELINES': {
		MongoTextComponent:  100,
		TextParserComponent: 200,
		MongoWordsComponent: 300,
	}}

	def _parse_wiki(self, topic, response):
		# get paragraph elements, and all of their children (boldface, anchor etc)
		response_chunks = response.css('p *::text').getall()
		if not response_chunks:
			raise CloseSpider(f"Wiki page for the topic '{topic}' contains no text (?!).")
		item = ChineseTextItem()
		item['collection'] = f"words_{topic}"
		item['url'] = unquote(response.url)  # back from percentage encoding to utf
		# get rid of spaces and reference numbers
		pattern = r"[\n\t]+|\[\d+\]"
		jumbo_string = "".join([sub(pattern, "", chunk) for chunk in response_chunks])
		item['text'] = jumbo_string
		return item

	def _topic_translation(self):
		topic = getattr(self, 'topic', None)
		# we should have the translation at this point
		client     = pymongo.MongoClient(self.settings['MONGODB_URI'])
		db         = client[self.settings['MONGODB_DB']]
		collection = self.settings['TRANSLATION_COLLECTION']
		# the second argument is projection, it specifies which arguments to return (1=return, 0=do not)
		ret = db[collection].find_one({'english': {'$eq': topic.replace("_", " ")}}, {'chinese': 1})
		client.close()
		if not ret or 'chinese' not in ret or not ret['chinese']:
			print("xxxxxxxxxxxxxxxxxxxxxxxxxxx")
			raise CloseSpider(f"Chinese translation for the topic '{topic}' not found in the local DB.")
		return ret['chinese']

	def start_requests(self):  # must return an iterable of Requests
		topic = set_topic(self)
		topic_chinese = self._topic_translation()
		print(f"TopicVocabSpider in start_requests, topic is: {topic}")
		url = f"https://{self.start_netloc}/zh-cn/{topic_chinese}"
		# scrapy.log has been deprecated alongside its functions in favor of explicit calls to the
		# Python standard logging.
		# self.log(f"request url: ***  {url}")
		print(f"request url: ***  {url}")
		yield scrapy.Request(url=url, callback=self.parse)

	def parse(self, response, **kwargs):  # called to handle the response downloaded
		""" This function parses Chinese language Wikipedia page related to the topic.
		@url https://zh.wikipedia.org/zh-cn/基因组
		@returns items 1
		@scrapes collection url text
		"""
		print(f"TopicVocabSpider in parse")
		topic = "blah"
		# topic = getattr(self, 'topic', "anon")
		# did we get Page not found (页面不存在) by any chance?
		# response.css('a.new::attr(title)').getall() # css does not support pattern matching
		# not a good idea - apparently there are always links which say "page not found":
		# not_found = response.xpath('//a[@class="new"][contains(@title, "页面不存在")]').get()
		# however  维基百科目前还没有与上述标题相同的条目 (Wikipedia currently does not have the entry)
		# text does not appear when the page with that title exists
		not_found = response.xpath('//*[contains(text(), "维基百科目前还没有与上述标题相同的条目")]').get()
		if not_found:
			raise CloseSpider(f"Wiki page for the topic '{topic}' not found.")
		# we're ok, format the return item
		return self._parse_wiki(topic, response)

# 网络搜寻

