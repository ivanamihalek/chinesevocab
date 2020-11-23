
# You can provide command line arguments to your spiders by using the -a option when running them:
# scrapy crawl plain -O plain.json -a topic=genome
# These arguments are passed to the Spider’s __init__ method and become spider attributes by default.

import scrapy
from urllib.parse import unquote

class PlainSpider(scrapy.Spider):
	name = "plain"  # must be unique within a project => note this is how we invoke it from the scrapy crawl command

	source_url = {
		"wiki":{"molecular_biology":"https://zh.wikipedia.org/zh-cn/分子生物学",
				"genome":"https://zh.wikipedia.org/zh-cn/基因組"},
		"baike":{"molecular_biology":"https://baike.baidu.com/item/分子生物学/126586",
				 "genome":"https://baike.baidu.com/item/基因组"}
	}

	def start_requests(self):  # must return an iterable of Requests
		topic = getattr(self, 'topic', None)
		if not topic:
			topic = "genome"
			setattr(self,  'topic', topic)
		urls = [pages[topic] for source, pages in self.source_url.items() if topic in pages]
		for url in urls:
			yield scrapy.Request(url=url, callback=self.parse)

	def parse(self, response, **kwargs):  # called to handle the response downloaded
		unquoted_url = unquote(response.url)
		self.log(f"response.url: ***  {response.url}")
		# write to file - usually that would not be what we want
		source = "anon"
		for src, pages in self.source_url.items():
			self.log(f'page: ***  {pages[self.topic]}')
			if response.url in pages[self.topic]: source = src
		filename = f'vocab-{source}-{self.topic}.html'
		with open(filename, 'wb') as f:
			f.write(response.body)
		self.log(f'Saved file {filename}')
