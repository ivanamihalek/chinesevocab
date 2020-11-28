#! /usr/bin/python3

# the runner recipe from https://docs.scrapy.org/en/latest/topics/practices.html
from sys import argv
from twisted.internet import reactor
from scrapy.crawler import CrawlerRunner
from scrapy.utils.project import get_project_settings
from chinesevocab.spiders.basic_vocab_spider import BasicVocabSpider
from chinesevocab.spiders.topic_vocab_spider import TopicVocabSpider


usage_statement = '''
	Using '{topic}' as default topic.
	You can change the topic by running: {cmd} <topic>.
'''


def main():
	settings = get_project_settings()
	runner = CrawlerRunner(settings)

	if len(argv) > 1:
		topic = argv[1]
	else:
		topic = "genome"
		print(usage_statement.format(topic=topic, cmd=argv[0]))

	# TODO: skip if we already have the basic vocab

	d = runner.crawl(BasicVocabSpider)
	d.addBoth(lambda _: reactor.stop())
	reactor.run()  # the script will block here until the crawling is finished

	settings.set("TOPIC", topic)
	# d = runner.crawl(TopicVocabSpider)
	# d.addBoth(lambda _: reactor.stop())
	# reactor.run()  # the script will block here until the crawling is finished


if __name__ == "__main__":
	main()