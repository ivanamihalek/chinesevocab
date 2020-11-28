# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

# useful for handling different item types with a single interface
import logging
import pymongo
from itemadapter import ItemAdapter

import re
import jieba
from chinesevocab.items import TokenSetItem

class TextParserComponent:

    def __init__(self):
        pass

    def _tokenize(self, item):
        # get rid of non-chinese characters
        matches = re.findall("[\u4e00-\u9FFF]", item['text'])
        chstr = "".join(matches)
        jieba.setLogLevel(logging.ERROR)
        return set(jieba.cut(chstr, cut_all=True))

    @classmethod
    def from_crawler(cls, crawler):
        return cls()

    def open_spider(self, spider):
        # print("open o spider <<<<<<<<<<<<<<<<<")
        pass

    def close_spider(self, spider):
        # print("close o spider <<<<<<<<<<<<<<<<<")
        pass

    def process_item(self, item, spider):
        # print("processing item<<<<<<<<<<<<<<<<<")
        processedItem = TokenSetItem()
        processedItem['tokens'] = self._tokenize(item)
        processedItem['collection'] = item['collection']
        return processedItem
