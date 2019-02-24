# -*- coding: utf-8 -*-

import scrapy
import os
import re, json, random, logging
import urllib, hashlib
import time, datetime
from django.forms import model_to_dict
from urllib import parse as urlparse
from datetime import timedelta
from scrapy.utils.python import to_bytes
from ..utils.url_type import parse_url_type
from .items import ImageItem


class BossSpider(scrapy.Spider):
    """
    lagou爬虫
    """
    name = "shentong_spider"

    custom_settings = {
        "FILES_STORE": "F:/shentong_images",
        "SOURCE_STORE":"F:/shentong_images/source",
        "DOWNLOAD_DELAY": 2,
        "RETRY_TIMES": 5,
        "DEPTH_LIMIT": 90,
        # "ROUNTINE_INTERVAL": 0,
        "CONCURRENT_REQUESTS": 32,
        "DOWNLOAD_TIMEOUT": 20,
        "MEDIA_ALLOW_REDIRECTS": True,
        "REDIRECT_ENABLED": False,
        # # Ensure use this Scheduler
        # "SCHEDULER": "scrapy_redis_bloomfilter.scheduler.Scheduler",
        #
        # Ensure all spiders share same duplicates filter through redis
        # "DUPEFILTER_CLASS": "source_spider.spiders.utils.dupefilters.BloomDupeFilter",
        #
        # # Redis URL
        # "REDIS_URL": 'redis://:abcABC123@47.101.214.74:6379/1',
        #
        # # Number of Hash Functions to use, defaults to 6
        # "BLOOMFILTER_HASH_NUMBER": 6,
        #
        # # Redis Memory Bit of Bloomfilter Usage, 30 means 2^30 = 128MB, defaults to 30
        # "BLOOMFILTER_BIT": 30,

        # # Persist
        # "SCHEDULER_PERSIST": True,
        "DOWNLOADER_MIDDLEWARES": {
            # 'source_spider.spiders.middlewares.RandomUserAgent': 501,
            # 'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
            "source_spider.spiders.shentong_spider.middlewares.SeleniumMiddleware": 503,
            # 'source_spider.spiders.middlewares.RandomProxy': 531,
            # 'source_spider.spiders.middlewares.ProcessAllExceptionMiddleware': 540
        },
        "SPIDER_MIDDLEWARES": {
            # 'source_spider.spiders.middlewares.RoutineSpiderMiddleware': 543,
            'scrapy.spidermiddlewares.depth.DepthMiddleware': 900,
        },
        "ITEM_PIPELINES": {
            "source_spider.spiders.shentong_spider.pipelines.VideoDownloadPipeline": 904
        },
    }

    def __init__(self, *args, **kwargs):
        super(BossSpider, self).__init__(*args, **kwargs)
        self.start_url = "https://image.baidu.com/search/index?tn=baiduimage&ipn=r&ct=201326592&cl=2&lm=-1&st=-1&fm=result&fr=&sf=1&fmq=1550928528156_R&pv=&ic=&nc=1&z=&hd=&latest=&copyright=&se=1&showtab=0&fb=0&width=&height=&face=0&istype=2&ie=utf-8&word=%E4%B8%B0%E5%AF%86%E8%BF%90%E5%8D%95"

    def start_requests(self):
        yield scrapy.Request(
            url=self.start_url, callback=self.parse_index, dont_filter=True, meta={"scrall": True}
        )

    def parse_index(self, response):
        url = response.url
        url_list = response.xpath("//div[@class='imgbox']//a[contains(@name,'pn')]/@href").extract()
        for url_item in [url_list[0]]:
            next_url = urlparse.urljoin(url, url_item)
            yield scrapy.Request(url=next_url, callback=self.parse_image)

    def parse_image(self, response):
        image_path = response.xpath("//img[@class='currentImg']/@src").extract_first()
        item = ImageItem()
        item["url"] = image_path
        item["name"] = str(int(time.time() * 1000)) + "."+image_path.split(".")[-1]
        yield item
