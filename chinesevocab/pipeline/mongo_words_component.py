# Define your item pipelines here

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


import pymongo

# for MongoDB docs see https://docs.mongodb.com/manual/installation/
# make sure mongo is running: sudo systemctl start mongod
# check running: sudo systemctl status mongod
from pymongo import UpdateOne, MongoClient
from pymongo.errors import BulkWriteError


class MongoWordsComponent:
    """ Stores individual words to local DB. """

    def __init__(self, mongo_uri, mongo_db, words_collection):
        """ Stores DB-related names. """

        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db
        self.generic_words_collection = words_collection+"_generic"

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI'),
            mongo_db=crawler.settings.get('MONGODB_DB', 'items'),
            words_collection=crawler.settings.get('WORDS_COLLECTION', 'words'),
        )

    def open_spider(self, spider):
        """ Opens DB connection. """

        self.client = MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]
        self.generic_words = set([doc["_id"] for doc in self.db[self.generic_words_collection].find()])

    def close_spider(self, spider):
        """ Closes DB connection. """

        self.client.close()

    def process_item(self, item, spider):
        """ Stores words DB. If already present, increases the counter.  """

        spider.logger.info(f"In process_item in MongoWordsComponent.")
        # the item now is a set of tokens (words)
        collection = item['collection']
        requests = []
        for token in item['tokens']:
            if token in self.generic_words: continue
            # we ant duplicates, because we will count the word frequency
            requests.append(UpdateOne({'_id': token}, {"$inc": {"count": 1}}, upsert=True))
        if requests:
            try:
                # this is mongo's batch
                # https://pymongo.readthedocs.io/en/stable/examples/bulk.html
                self.db[collection].bulk_write(requests, ordered=False)
            except BulkWriteError as bwe:
                spider.logger.error(bwe.details)
        return item
