

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


# You can provide command line arguments to your spiders by using the -a option when running them:
# scrapy crawl extended -a topic=genome
# These arguments are passed to the Spider’s __init__ method and become spider attributes by default.
# Note: by default, Scrapy filters out duplicated requests to URLs already visited.
# scrapy crawl extended -a topic=genome  2>&1 | grep "\[extended\] INFO"

import re

import pymongo
import scrapy
from scrapy import Spider
from scrapy.linkextractors import LinkExtractor

from urllib.parse import unquote, urlparse

from chinesevocab.pipeline.mongo_text_component import MongoTextComponent
from chinesevocab.pipeline.text_parser_component import TextParserComponent
from chinesevocab.pipeline.mongo_words_component import MongoWordsComponent
from chinesevocab.spiders.vocab_spider import VocabSpider


class ExtendedTopicVocabSpider(VocabSpider):
	# for the purposes of this demo, the extended search consists
	# of the first three pages returned by google
	name = "extended"
	start_netloc = "www.google.com"
	number_of_start_pages = 3
	# note  custom_settings has to be defined as a class (not an instance) attribute
	custom_settings = {'ITEM_PIPELINES': {
		MongoTextComponent:  100,
		TextParserComponent: 200,
		MongoWordsComponent: 300},
		'ROBOTSTXT_OBEY': False  # let's just ask for a page or two
	}
	domains_not_allowed = ['upload.wikimedia.org', 'hr.wikipedia.org',
	                       'accounts.google.com', 'baike.baidu.com']
	# handle page not found explicitly
	# (https://docs.scrapy.org/en/latest/topics/spider-middleware.html#module-scrapy.spidermiddlewares.httperror)
	handle_httpstatus_list = [404]

	link_extractor = LinkExtractor()

	def _strip_link(self, compound_link):
		compound_pieces = compound_link.split("=")
		if len(compound_pieces)<2: return None
		if compound_pieces[1][:4] != "http": return None
		url = compound_pieces[1].split("&")[0]
		parsed_url = urlparse(url)
		if parsed_url.netloc in self.domains_not_allowed: return None
		if parsed_url.path.split(".")[-1].lower() in ["image", "png", "jpg", "gif", "pdf"]: return None
		return url

	def _scrub_url(self, url):
		unquoted_url = unquote(unquote(url))  # not sure what's with this, but it works
		parsed = urlparse(unquoted_url)
		if parsed.netloc in ["zh.wikipedia.org", "zh.m.wikibooks.org"]:
			# let's take Mainland Chinese if we can
			pathpieces = parsed.path.split("/")
			# this will be for example ['', 'wiki', '基因組學'] or  ['', 'zh-hans', '基因組學']
			# we want the second element of the path  replaced by zh_cn
			pathpieces[1] = "zh-cn"
			new_url = "/".join([parsed.scheme+":/", parsed.netloc]+pathpieces)
			return new_url
		else:
			return unquoted_url

	def _extract_links(self, response):
		for link in self.link_extractor.extract_links(response):
			# google is going back to its whatever wih the mangled link
			# I just need the resource url (nice of them to keep it  unmangled)
			url = self._strip_link(link.url)
			if not url: continue
			clean_url = self._scrub_url(url)
			if self._page_already_in_db(url):
				self.logger.info(f"***** {url} already seen")
				continue
			yield scrapy.Request(url=clean_url, callback=self.parse)

	def start_requests(self):  # must return an iterable of Requests
		""" A Scrapy framework hook. """
		if not self.topic:
			self.logger.error("Topic not set in TranslationSpider. ")
			self.logger.error("If running this spider only, you can set it on cmd line with -a topic=<topic>.")
			return None
		self.logger.info(f"\nExtendedTopicVocabSpider in start_requests, topic is: {self.topic}.")
		topic_chinese = self._topic_translation()
		if not topic_chinese:  # never figured out how to catch  an exception thrown here
			self.logger.error(f"No topic translation found for {self.topic}.")
			return
		else:
			path = f"search?q={topic_chinese}"
			urls = [f"https://{self.start_netloc}/{path}&start={i*10}" for i in range(self.number_of_start_pages)]
			for url in urls:
				self.logger.info(f"request url: ***  {url}")
				yield scrapy.Request(url=url, callback=self.parse)

	def parse(self, response, **kwargs):
		""" A Scrapy framework hook. Follows links from a bigger search engine (Google) and extracts chinese text.
		@url https://zh.wikipedia.org/zh-cn/基因组
		@returns items 1
		@scrapes collection url text
		"""
		if response.status == 404:  # page not found
			return
		# not sure how to check the extracted links
		if urlparse(response.url).netloc == self.start_netloc:
			# use google pages to extract links to follow
			self.logger.info(f"extracting links from  {response.url}")
			return self._extract_links(response)
		else:
			# we should be on a page with something useful
			self.logger.info(f"extracting content from  {response.url}")
			return self._extract_chinese_content(response)  # inherited from vocab_spider
