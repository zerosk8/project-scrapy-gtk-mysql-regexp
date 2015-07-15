# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class WallhavenItem(scrapy.Item):
    name = scrapy.Field()
    width = scrapy.Field()
    height = scrapy.Field()
    format = scrapy.Field()
    url = scrapy.Field()
    query = scrapy.Field()
