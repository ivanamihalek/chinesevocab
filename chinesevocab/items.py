# Define here the models for your scraped items
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
    pass

class TokenSetItem(Item):
    tokens = Field()
