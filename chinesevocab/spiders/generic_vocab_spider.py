

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


# to use directly - though here running from fun.py would be preferred
# scrapy crawl generic
# These arguments are passed to the Spider’s __init__ method and become spider attributes by default.

import scrapy

from chinesevocab.items import TokenSetItem
from chinesevocab.pipeline.mongo_words_component import MongoWordsComponent

# TODO patch for
# 一个
# 这种
# 一种
# 这个
# 不是


class GenericVocabSpider(scrapy.Spider):
	# name must be unique within a project
	# => note this is how we invoke it from the scrapy crawl command
	name = "generic"
	# note  custom_settings has to be defined as a class (not an instance) attribute
	custom_settings = {'ITEM_PIPELINES': {MongoWordsComponent: 300}}

	# looks like I cannot scrape github proper - they prefer using their API (see https://github.com/robots.txt)
	# today I'll just start with the list of pages that I know contain the generic mandarin vocab (HSK 1-hsk_max_level)
	# these pages are plain text, so no html/css parsing involved
	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		self.collection = "words_generic"  # the collection to store in

	def start_requests(self):  # must return an iterable of Requests
		urls = []
		# wikipedia most frequent words
		raw_pages_domain = "https://en.wiktionary.org"
		path = "wiki/Appendix:Mandarin_Frequency_lists"
		freq_max = 2  # this is 2 thousand
		wiki_pages = [f"{raw_pages_domain}/{path}/{i*1000+1}-{(i+1)*1000}" for i in range(freq_max)]
		urls.extend(wiki_pages)
		# HSK words
		raw_pages_domain = "https://raw.githubusercontent.com"
		path = "glxxyz/hskhsk.com/main/data/lists"
		hsk_max_level = 5
		hsk_pages = [f"{raw_pages_domain}/{path}/HSK%20Official%202012%20L{i+1}.txt" for i in range(hsk_max_level)]
		urls.extend(hsk_pages)
		for url in urls:
			yield scrapy.Request(url=url, callback=self.parse)

	def parse(self, response, **kwargs):  # called to handle the response downloaded
		""" This function parses pages containing lists of words.
		@url https://en.wiktionary.org/wiki/Appendix:Mandarin_Frequency_lists/1-1000
		@returns items 1
		@scrapes collection tokens
		@url https://raw.githubusercontent.com/glxxyz/hskhsk.com/main/data/lists/HSK%20Official%202012%20L3.txt
		@returns items 1
		@scrapes collection tokens
		"""
		print(f"in generic_vocab_spider parse, {response.url}")
		item = TokenSetItem()
		# the components that should act on this item
		item['collection'] = self.collection
		parse_text = response.url[-4:] == ".txt"
		if parse_text:
			item['tokens'] = response.body.decode("utf-8-sig").split()
		else:  # parse wiki
			item['tokens'] = response.css("span.Hans ::text").getall()
		yield item


