import scrapy


class ImageItem(scrapy.Item):
    url = scrapy.Field()
    name = scrapy.Field()
