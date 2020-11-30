
# You can provide command line arguments to your spiders by using the -a option when running them:
# scrapy crawl extended -a topic=genome
# These arguments are passed to the Spider’s __init__ method and become spider attributes by default.
# Suggested use scrapy crawl plain -O plain.json -a topic=genome 2>&1 | grep DEBUG > debug.log
# Note: by default, Scrapy filters out duplicated requests to URLs already visited.

import re

import pymongo
import scrapy
from scrapy.exceptions import CloseSpider
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
		ret = db[collection].find_one({'english': {'$eq': topic.replace("_", " ")}}, {'chinese': 1})
		if not ret or 'chinese' not in ret or not ret['chinese']:
			raise CloseSpider(f"Chinese translation for the topic '{topic}' not found in the local DB")
		client.close()
		return ret['chinese']

	def _strip_link(self, compound_link):
		compound_pieces = compound_link.split("=")
		if len(compound_pieces)<2: return None
		if compound_pieces[1][:4] != "http": return None
		url = compound_pieces[1].split("&")[0]
		parsed_url = urlparse(url)
		if parsed_url.netloc in self.domains_not_allowed: return None
		if parsed_url.path.split(".")[-1].lower() in ["image", "png", "jpg", "gif", "pdf"]: return None
		return url

	def _scrub(self, url):
		unquoted_url = unquote(unquote(url))  # not sure what's with this, but it works
		parsed = urlparse(unquoted_url)
		if parsed.netloc in ["zh.wikipedia.org", "zh.m.wikibooks.org"]:
			# let's take Mainland Chinese if we can
			pathpieces = parsed.path.split("/")
			# this will be for example ['', 'wiki', '基因組學'] or  ['', 'zh-hans', '基因組學']
			# we want the second element of the path  replaced by zh_cn
			pathpieces[1] = "zh-cn"
			new_url = "/".join([parsed.netloc]+pathpieces)
			return new_url
		else:
			return unquoted_url

	def _extract_links(self, response):
		# TODO: check with the database if we already have the contents of this link
		# TODO: check with the database if we have enough words
		unquoted_url = unquote(unquote(response.url))
		print(f"\nxxxxxxxxxxxxxxxxxxxxxxxxx\n{unquoted_url}")
		for link in self.link_extractor.extract_links(response):
			# google is going back to its whatever wih the link
			# I just need the link
			# nice of them to keep the link unmangled
			url = self._strip_link(link.url)
			if not url: continue
			clean_url = self._scrub(url)
			print("moving to ", clean_url)
			yield scrapy.Request(url=url, callback=self.parse)

	def _package(self, unquoted_url, jumbo_string):
		topic = self._get_topic()
		item = ChineseTextItem()
		item['collection'] = f"words_{topic}"
		item['url'] = unquoted_url
		item['text'] = jumbo_string
		return item

	def _extract_content(self, response):
		unquoted_url = unquote(unquote(response.url))
		print(f"\n000000000000000000000000000000\n{unquoted_url}")
		response_chunks = response.css('*::text').getall()
		if not response_chunks: return
		# how much of that is actually chinese?
		cc_pattern = r"[\u4e00-\u9FFF]" # chinese characters
		space_pattern = r"[\n\t]+|\[\d+\]"
		usable_chunks = []
		for chunk in response_chunks:
			# get rid of spaces and reference numbers
			spaced_out_chunk = re.sub(space_pattern, "", chunk)
			if len(spaced_out_chunk) == 0: continue
			number_of_chinese_characters = len(re.findall(cc_pattern, spaced_out_chunk))
			if number_of_chinese_characters/len(spaced_out_chunk) < .8: continue
			usable_chunks.append(spaced_out_chunk)
		return self._package(unquoted_url, "".join(usable_chunks))

	def start_requests(self):  # must return an iterable of Requests
		topic_chinese = self._topic_translation()
		path = f"search?q={topic_chinese}"
		urls = [f"https://{self.start_netloc}/{path}&start={i*10}" for i in range(self.number_of_start_pages)]
		for url in urls:
			yield scrapy.Request(url=url, callback=self.parse)

	def parse(self, response, **kwargs):
		topic = self._get_topic()
		collection = f"words_{topic}"  # the collection we will be storing this into
		# this is working in python3 shell and for response.url
		unquoted_url = unquote(response.url)  # back from percentage encoding to utf
		if urlparse(response.url).netloc == self.start_netloc:
			return self._extract_links(response)
		else:
			return self._extract_content(response)
