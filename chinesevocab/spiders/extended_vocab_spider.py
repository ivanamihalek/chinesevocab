
# You can provide command line arguments to your spiders by using the -a option when running them:
# scrapy crawl extended -a topic=genome
# These arguments are passed to the Spider’s __init__ method and become spider attributes by default.
# Suggested use scrapy crawl plain -O plain.json -a topic=genome 2>&1 | grep DEBUG > debug.log

import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor

from chinesevocab.items import ChineseTextItem
from urllib.parse import unquote, urlparse

from chinesevocab.pipeline.mongo_text_component import MongoTextComponent
from chinesevocab.pipeline.text_parser_component import TextParserComponent
from chinesevocab.pipeline.mongo_words_component import MongoWordsComponent


class ExtendedVocabSpider(scrapy.Spider):
	# name must be unique within a project
	# => note this is how we invoke it from the scrapy crawl command
	name = "extended"
	# note  custom_settings has to be defined as a class (not an instance) attribute
	# custom_settings = {'ITEM_PIPELINES': {
	# 	MongoTextComponent:  100,
	# 	TextParserComponent: 200,
	# 	MongoWordsComponent: 300},
	# 	'ROBOTSTXT_OBEY': False  # let's just ask for a page or two
	# }
	custom_settings = {'ROBOTSTXT_OBEY': False  # let's just ask for a page or two
	}
	link_extractor = LinkExtractor()
	start_urls = ['http://google.com/search?q=基因组']
	domains_not_allowed = ['upload.wikimedia.org', 'hr.wikipedia.org', 'accounts.google.com']

	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		print("hullo")

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
		# this is working in python3 shell and for response.url
		# unquoted_url = unquote(response.url)  # back from percentage encoding to utf
		for link in self.link_extractor.extract_links(response):
			# google is going back to its whatever wih the link
			# I just need the link
			# nice of them to keep the link unmangled
			url = self._strip_link(link.url)
			if not url: continue
			print(url)

