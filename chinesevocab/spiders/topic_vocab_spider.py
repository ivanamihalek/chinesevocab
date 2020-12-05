

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
# scrapy crawl topic -a topic=genome
# These arguments are passed to the Spider’s __init__ method and become spider attributes by default.
# Grepping for info log:
# scrapy crawl topic -a topic=genome  2>&1 | grep "\[topic\] INFO"

import scrapy
from scrapy.exceptions import CloseSpider

from chinesevocab.items import ChineseTextItem
from urllib.parse import unquote
from re import sub

from chinesevocab.pipeline.mongo_text_component import MongoTextComponent
from chinesevocab.pipeline.text_parser_component import TextParserComponent
from chinesevocab.pipeline.mongo_words_component import MongoWordsComponent
from chinesevocab.spiders.vocab_spider import VocabSpider


class TopicVocabSpider(VocabSpider):

	# name must be unique within a project
	# => note this is how we invoke it from the scrapy crawl command
	name = "topic"
	start_netloc = "zh.wikipedia.org"
	# note  custom_settings has to be defined as a class (not an instance) attribute
	custom_settings = {
		'ITEM_PIPELINES': {
			MongoTextComponent:  100,
			TextParserComponent: 200,
			MongoWordsComponent: 300},
	}
	# handle page not found explicitly
	# (https://docs.scrapy.org/en/latest/topics/spider-middleware.html#module-scrapy.spidermiddlewares.httperror)
	handle_httpstatus_list = [404]

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

	def start_requests(self):  # must return an iterable of Requests
		if not self.topic:
			self.logger.error("Topic not set in TranslationSpider. ")
			self.logger.error("If running this spider only, you can set it on cmd line with -a topic=<topic>.")
			return
		self.logger.info(f"TopicVocabSpider in start_requests, topic is: {self.topic}")
		topic_chinese = self._topic_translation()
		if not topic_chinese:  # never figured out how to catch  an exception thrown here
			self.logger.error(f"No topic translation found for {self.topic}.")
			return

		else:
			url = f"https://{self.start_netloc}/zh-cn/{topic_chinese}"
			if self._page_already_in_db(url):
				self.logger.info(f"{url} visited already")
				return
			else:
				self.logger.info(f"request url: ***  {url}")
				yield scrapy.Request(url=url, callback=self.parse)

	def parse(self, response, **kwargs):  # called to handle the response downloaded
		""" This function parses Chinese language Wikipedia page related to the topic.
		@url https://zh.wikipedia.org/zh-cn/基因组
		@returns items 1
		@scrapes collection url text
		"""
		self.logger.info(f"TopicVocabSpider in parse.")
		topic = getattr(self, 'topic', "anon")
		if response.status == 404:  # page not found
			# CloseSpider can be raised in spider callback, i.e. here
			raise CloseSpider(f"Wiki page for the topic '{topic}' not found.")
		# we're ok, format the return item
		return self._parse_wiki(topic, response)

