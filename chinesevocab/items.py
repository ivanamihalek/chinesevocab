# Define here the models for your scraped items

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


#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

from scrapy.item import Item, Field


# an item is not necessarily model (a db entry), though it can be
# this is just how the data is passed down the pipeline
# from https://docs.scrapy.org/en/latest/topics/items.html :
# The Field class is just an alias to the built-in dict class and doesn’t provide any extra functionality or attributes.
# In other words, Field objects are plain-old Python dicts.
class ChineseTextItem(Item):
    # define the fields for your item here like:
    # source - there did this get from
    url = Field()
    # text chunk
    text = Field()
    # the collection we ant to store it in (generic or  one of topics)
    collection = Field()


class TokenSetItem(Item):
    # the collection we ant to store it in (generic or  one of topics)
    collection = Field()
    tokens = Field()


class TranslationItem(Item):
    chinese = Field()
    pinyin = Field()
    english = Field()

