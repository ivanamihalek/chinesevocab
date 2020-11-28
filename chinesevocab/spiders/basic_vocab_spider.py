
# to use directly - though here runnig from fun.py would be preferred
# scrapy crawl basic
# These arguments are passed to the Spider’s __init__ method and become spider attributes by default.

import scrapy

from chinesevocab.items import TokenSetItem
from chinesevocab.pipeline.mongo_words_component import MongoWordsComponent


class BasicVocabSpider(scrapy.Spider):
	# name must be unique within a project
	# => note this is how we invoke it from the scrapy crawl command
	name = "basic"
	# note  custom_settings has to be defined as a class (not an instance) attribute
	custom_settings = {'ITEM_PIPELINES': {MongoWordsComponent: 300}}

	# looks like I cannot scrape github proper - they prefer using their API (see https://github.com/robots.txt)
	# today I'll just start with the list of pages that I know contain the basic mandarin vocab (HSK 1-3)
	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		raw_pages_domain = "https://raw.githubusercontent.com"
		path = "glxxyz/hskhsk.com/main/data/lists"
		self.start_urls = [f"{raw_pages_domain}/{path}/HSK%20Official%202012%20L{i+1}.txt" for i in range(3)]
		self.collection = "words_basic"  # the collection we will be storing this into

	def parse(self, response, **kwargs):  # called to handle the response downloaded
		print(f"in basic_vocab_spider parse")
		# this page serves raw text, containing only the words that I need
		item = TokenSetItem()
		# the components that should act on this item
		item['collection'] = self.collection
		item['tokens'] = response.body.decode("utf-8-sig").split()
		print(f"in basic_vocab_spider parse - number of tokens: {len(item['tokens'])}")
		yield item


