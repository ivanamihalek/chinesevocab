
# You can provide command line arguments to your spiders by using the -a option when running them:
# scrapy crawl translation -a topic=genome
# These arguments are passed to the Spider’s __init__ method and become spider attributes by default.
# Suggested use scrapy crawl plain -O plain.json -a topic=genome 2>&1 | grep DEBUG > debug.log

import scrapy
from scrapy.exceptions import CloseSpider

from chinesevocab.items import TranslationItem

from chinesevocab.spiders.vocab_spider import VocabSpider


class TranslationSpider(VocabSpider):
	# for the purposes of this demo, the extended search consists
	# of the first three pages returned by google
	name = "translation"
	start_netloc = "www.linguabot.com"

	def start_requests(self):  # must return an iterable of Requests
		# if we started this spider only from the command line, but did not provide the topic, for example
		if not self.topic:
			print("Topic not set in TranslationSpider. ")
			print("If running this spider only, you can set it on cmd line with -a topic=<topic>.")
			return None
		print(f"TranslationSpider in start_requests, topic is: {self.topic}")
		url = f"http://{self.start_netloc}/dictLookup.php?word={self.topic.replace('_', '+')}"
		# scrapy.log has been deprecated alongside its functions in favor of explicit calls to the
		# Python standard logging.
		yield scrapy.Request(url=url, callback=self.parse)

	def parse(self, response, **kwargs):
		""" This function parses a translation page.
		@url http://www.linguabot.com/dictLookup.php?word=genome
		@returns items 1
		@scrapes chinese english pinyin
		"""
		print(f"TranslationSpider in parse")
		# this is for the purposes of contract test runs
		# in an actual run we should not get to here if the self.topic is not set
		if getattr(self, "topic", None) is None:  self.topic = "genome"
		query = self.topic.replace("_", " ").lower()
		# TODO this is somewhat simpleminded in assuming that
		# TODO  we are going to have one and exactly one translation
		# tr 4 td's the fist is hanzi, the third english
		# there are some anchor labels, so we just use *, rather than td
		item = None
		for row in response.css("tr"):
			cols = row.css("td *::text").getall()
			if not cols or len(cols)!=4: continue
			[chinese, pinyin, english, english_pronunciation] = cols
			english = english.lower()
			if english == query:
				item = TranslationItem()
				item['chinese'] = chinese
				item['english'] = english
				item['pinyin'] = pinyin.replace("[", "").replace("]", "").strip()
				print(f"{english} ---> {chinese}")
				break
		if not item:  # the rest of the pipeline depends on it, so we cannot move on without it
			raise CloseSpider(f"Chinese translation for the topic '{self.topic}' not found.")
		else:
			self._store_translation(item)
		return item  # again I need to return this item for the purposes of (contract) testing
