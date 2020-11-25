
# You can provide command line arguments to your spiders by using the -a option when running them:
# scrapy crawl plain -O plain.json -a topic=genome
# These arguments are passed to the Spider’s __init__ method and become spider attributes by default.
# Suggested use scrapy crawl plain -O plain.json -a topic=genome 2>&1 | grep DEBUG > debug.log

import scrapy
from chinesevocab.items import ChineseTextItem
from urllib.parse import unquote
from re import sub


class PlainSpider(scrapy.Spider):
	# name must be unique within a project
	# => note this is how we invoke it from the scrapy crawl command
	name = "plain"

	source_url = {
		"wiki": {"molecular_biology":"https://zh.wikipedia.org/zh-cn/分子生物学",
				"genome": "https://zh.wikipedia.org/zh-cn/基因組"},
		"baike": {"molecular_biology":"https://baike.baidu.com/item/分子生物学/126586",
				 "genome": "https://baike.baidu.com/item/基因组"}
	}

	def _process_text_chunk(self, jumbo_string):
		print("Im in _process_text_chunk <<<<<<<<<<<<<<<<<<")
		item = ChineseTextItem()
		item['chunk'] = jumbo_string[:20]
		return item

	def _parse_wiki(self, response):
		# get paragraph elements, and all of their children (boldface, anchor etc)
		response_chunks = response.css('p *::text').getall()
		if not response_chunks: return
		# get rid of spaces and reference numbers
		pattern = r"[\n\t]+|\[\d+\]"
		jumbo_string = "".join([sub(pattern, "", chunk) for chunk in response_chunks])
		print(jumbo_string[0:100])
		return self._process_text_chunk(jumbo_string)

	def _file_write(self, source, topic, response):
		filename = f'vocab-{source}-{topic}.html'
		with open(filename, 'wb') as f:
			f.write(response.body)
		self.log(f'Saved file {filename}')

	def start_requests(self):  # must return an iterable of Requests
		topic = getattr(self, 'topic', None)
		if not topic:
			topic = "genome"
			setattr(self,  'topic', topic)
		urls = [pages[topic] for source, pages in self.source_url.items() if topic in pages]
		for url in urls:
			self.log(f"request url: ***  {url}")
			yield scrapy.Request(url=url, callback=self.parse)

	def parse(self, response, **kwargs):  # called to handle the response downloaded
		unquoted_url = unquote(response.url)  # back from percentage encoding to utf
		topic = getattr(self, 'topic', "no_topic")
		self.log(f"response.url: ***  {unquoted_url}")
		# write to file - usually that would not be what we want
		source = "anon"
		for src, pages in self.source_url.items():
			self.log(f'page: ***  {pages[topic]}')
			if unquoted_url in pages[topic]: source = src
		if source == "wiki":
			return self._parse_wiki(response)
		elif source == "baike":
			self.log(f'As of Nov 2020 baike forbids robots')
			return
		else:
			return self._file_write(source, topic, response)
