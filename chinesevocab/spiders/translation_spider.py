
# You can provide command line arguments to your spiders by using the -a option when running them:
# scrapy crawl translation -a topic=genome
# These arguments are passed to the Spider’s __init__ method and become spider attributes by default.
# Suggested use scrapy crawl plain -O plain.json -a topic=genome 2>&1 | grep DEBUG > debug.log

import scrapy
from scrapy.exceptions import CloseSpider

from chinesevocab.items import ChineseTextItem, TranslationItem

from chinesevocab.pipeline.mongo_translation_component import MongoTranslationComponent


class TranslationSpider(scrapy.Spider):
	# for the purposes of this demo, the extended search consists
	# of the first three pages returned by google
	name = "translation"
	# note  custom_settings has to be defined as a class (not an instance) attribute
	custom_settings = {'ITEM_PIPELINES': {MongoTranslationComponent: 300}}

	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		topic = getattr(self, 'topic', None)
		if not topic:
			topic = "genome"
			setattr(self,  'topic', topic)
		# for translation ping linguabot
		self.start_urls = [f"http://www.linguabot.com/dictLookup.php?word={topic.replace('_', '+')}"]

	def start_requests(self):  # must return an iterable of Requests
		for url in self.start_urls:
			topic = url.split("=")[-1]
			# scrapy.log has been deprecated alongside its functions in favor of explicit calls to the
			# Python standard logging.
			# self.log(f"request url: ***  {url}")
			yield scrapy.Request(url=url, callback=self.parse, meta={'query': topic})

	def parse(self, response, **kwargs):
		query = response.meta.get('query').replace("+", " ").lower()
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
				break
		if not item:  # the rest of the pipeline depends on it, so we cannot move on without it
			raise CloseSpider(f"Chinese translation for the topic '{query}' not found")
		return item
