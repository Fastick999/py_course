# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class SteamSpiderItem(scrapy.Item):
    # define the fields for your item here like:
    game = scrapy.Field()
    path = scrapy.Field()
    reviews_count = scrapy.Field()
    reviews_rate = scrapy.Field()
    release_date = scrapy.Field()
    developers = scrapy.Field()
    tags = scrapy.Field()
    price = scrapy.Field()
    platforms = scrapy.Field()
