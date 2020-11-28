
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


class TopicVocabSpider(scrapy.Spider):
	# name must be unique within a project
	# => note this is how we invoke it from the scrapy crawl command
	name = "topic"
	# note  custom_settings has to be defined as a class (not an instance) attribute
	custom_settings = {'ITEM_PIPELINES': {
		MongoTextComponent:  100,
		TextParserComponent: 200,
		MongoWordsComponent: 300,
	}}

	source_url = {
		"wiki": {"molecular_biology": "https://zh.wikipedia.org/zh-cn/分子生物学",
		         "genome": "https://zh.wikipedia.org/zh-cn/基因組"},
		"baike": {"molecular_biology": "https://baike.baidu.com/item/分子生物学/126586",
		          "genome": "https://baike.baidu.com/item/基因组"}
	}

	def _process_text_chunk(self, item, jumbo_string):
		item['text'] = jumbo_string
		return item

	def _parse_wiki(self, item, response):
		# get paragraph elements, and all of their children (boldface, anchor etc)
		response_chunks = response.css('p *::text').getall()
		if not response_chunks: return
		# get rid of spaces and reference numbers
		pattern = r"[\n\t]+|\[\d+\]"
		jumbo_string = "".join([sub(pattern, "", chunk) for chunk in response_chunks])
		return self._process_text_chunk(item, jumbo_string)

	def _file_write(self, source, topic, response):
		filename = f'vocab-{source}-{topic}.html'
		with open(filename, 'wb') as f:
			f.write(response.body)

	def start_requests(self):  # must return an iterable of Requests
		topic = getattr(self, 'topic', None)
		if not topic:
			topic = "genome"
			setattr(self,  'topic', topic)
		urls = [pages[topic] for source, pages in self.source_url.items() if topic in pages]
		for url in urls:
			# scrapy.log has been deprecated alongside its functions in favor of explicit calls to the
			# Python standard logging.
			# self.log(f"request url: ***  {url}")
			print(f"request url: ***  {url}")
			yield scrapy.Request(url=url, callback=self.parse)

	def parse(self, response, **kwargs):  # called to handle the response downloaded
		unquoted_url = unquote(response.url)  # back from percentage encoding to utf
		topic = getattr(self, 'topic', "anon")
		source = "anon"
		for src, pages in self.source_url.items():
			if unquoted_url in pages[topic]: source = src
		if source == "wiki":
			item = ChineseTextItem()
			item['collection'] = f"words_{topic}"
			item['url'] = unquoted_url
			print("in topic_vocab_spider process")
			return self._parse_wiki(item, response)
		elif source == "baike":
			self.log(f'As of Nov 2020 baike forbids robots')
			return
		else:
			# write to file - usually that would not be what we want
			return self._file_write(source, topic, response)
