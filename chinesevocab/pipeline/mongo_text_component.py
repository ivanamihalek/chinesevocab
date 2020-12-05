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


class MongoTextComponent:
    """ Stores extracted text chunks, together with the source url, in the local DB. """

    def __init__(self, mongo_uri, mongo_db, mongo_collection):
        """ Stores DB-related names. """

        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db
        self.collection = mongo_collection

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGODB_URI'),
            mongo_db=crawler.settings.get('MONGODB_DB', 'items'),
            mongo_collection=crawler.settings.get('TEXT_COLLECTION', 'text_chunks'),
        )

    def open_spider(self, spider):
        """ Opens DB connection. """

        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]

    def close_spider(self, spider):
        """ Closes DB connection. """

        self.client.close()

    def process_item(self, item, spider):
        """ Stores text chunk and url in the local DB. """

        spider.logger.info("In process_item in MongoTextComponent.")
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
        self.db[self.collection].find_one_and_update(filter, update, upsert=True)
        return item
