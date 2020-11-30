# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

# useful for handling different item types with a single interface
import logging
import pymongo
from itemadapter import ItemAdapter


# for MongoDB dos see https://docs.mongodb.com/manual/installation/
# make sure mongo is running: sudo systemctl start mongod
# check running: sudo systemctl status mongod
from pymongo import UpdateOne
from pymongo.errors import BulkWriteError


class MongoWordsComponent:

    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI'),
            mongo_db=crawler.settings.get('MONGODB_DB', 'items'),
        )

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]
        # it might be faster to just read in the glyphs from the basic vocab here - there  shouldn't be that many
        # TODO read the collection name from the settings
        self.basic_words = set([doc["glyphs"] for doc in self.db["words_basic"].find()])

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        # the item now is a set of tokens (words)
        collection = item['collection']
        requests = []
        for token in set(item['tokens']).difference(self.basic_words):
             requests.append(UpdateOne({'glyphs': token}, {'$set': {'glyphs': token}}, upsert=True))
        if requests:
            try:
                # this is mongo's batch
                # https://pymongo.readthedocs.io/en/stable/examples/bulk.html
                self.db[collection].bulk_write(requests, ordered=False)
            except BulkWriteError as bwe:
                print(bwe.details)  # TODO where's the logger handle
        return item
