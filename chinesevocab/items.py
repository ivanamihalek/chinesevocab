# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

from scrapy.item import Item, Field


# an item is not necessarily model (a db entry), though it can be
# this is just how the data is passed down the pipeline
class ChineseTextItem(Item):
    # define the fields for your item here like:
    chunk = Field()
    # TODO - add source
    pass

