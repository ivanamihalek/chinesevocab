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
class MongoTextComponent:
    # this assumes I'm feeding only into this collection
    collection_name = 'text_chunks'

    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI'),
            mongo_db=crawler.settings.get('MONGODB_DB', 'items')
        )

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        # note the insert/update/upsert
        # if nonexistent, the DB will be created
        # without checking: insert_one(ItemAdapter(item).asdict())
        # find or update:
        # def find_one_and_update(self, filter, update,
        #                     projection=None, sort=None, upsert=False, etc ...)
        # filter: A query that matches the document to update.
        # update: The update operations to apply (increase, set, rename, etc.)
        # For the operators see  https://docs.mongodb.com/manual/reference/operator/update-field/)
        # upsert: When ``True``, inserts a new document if no document matches the query.
        filter = {'url': item['url']}
        update = {'$set': {'text': item['text']}}
        self.db[self.collection_name].find_one_and_update(filter, update, upsert=True)
        return item
