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
from .models import YYModel, YYModelMeta
from ..utils.url_type import parse_url_type


class MovieSpider(scrapy.Spider):
    """
    yy爬虫
    """
    name = "yy_spider"

    custom_settings = {
        "FILES_STORE": "F:/video",
        "DOWNLOAD_DELAY": 0.1,
        "RETRY_TIMES": 1,
        "DEPTH_LIMIT": 90,
        "ROUNTINE_INTERVAL": 60 * 60 * 24 * 2,
        "CONCURRENT_REQUESTS": 32,
        "DOWNLOAD_TIMEOUT": 20,
        "MEDIA_ALLOW_REDIRECTS": True,
        "DOWNLOADER_MIDDLEWARES": {
            'source_spider.spiders.middlewares.RandomUserAgent': 501,
            'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
            # "source_spider.spiders.middlewares.SeleniumMiddleware": 503
            'source_spider.spiders.middlewares.AddRefer': 510
        },
        "SPIDER_MIDDLEWARES": {
            'source_spider.spiders.middlewares.RoutineSpiderMiddleware': 543,
            'scrapy.spidermiddlewares.depth.DepthMiddleware': 900,
        },
        "ITEM_PIPELINES": {
            "source_spider.spiders.video_spider.pipelines.VideoDownloadPipeline": 904
        },
    }

    def __init__(self, *args, **kwargs):
        super(MovieSpider, self).__init__(*args, **kwargs)
        self.start_url = "http://www.yzlu.one/videos?o= &page={}"
        self.end_page = 284

    def start_requests(self):
        for i in range(1, self.end_page):
            yield scrapy.Request(
                url=self.start_url.format(i), callback=self.parse_index, dont_filter=True,
            )

    def parse_index(self, response):
        url = response.url
        parents_node = response.xpath('//div[@class="container"]//div[contains(@class,"well")]/a/@href').extract()

        for sub_node in parents_node:
            sub_url = urlparse.urljoin(url, sub_node)
            yield scrapy.Request(url=sub_url, meta={"referer": url}, callback=self.parse_detail)

    def parse_detail(self, response):
        url = response.url
        title = response.xpath('//h3/text()').extract_first()
        source = response.xpath('//source/@src').extract_first()
        yield scrapy.Request(url=source, callback=self.parse_video, meta={"title": title, "url": url})

    def parse_video(self, response):
        text = response.text
        url = response.url
        if text:
            text = text.split("\n")[-1]
            url = url.replace("index.m3u8", text)
            yield scrapy.Request(url=url, callback=self.parse_video_fin, meta=response.meta)

    def parse_video_fin(self, response):
        text = response.text
        title = response.meta.get("title")
        source_url = response.meta.get("url")
        urls = []
        texts = []
        url = response.url
        if text:
            text = text.split("\n")
            for item in text:
                if item.endswith("ts"):
                    new_url = url.replace("index.m3u8", item)
                    new_text = item.replace(".ts", "")
                    urls.append(new_url)
                    texts.append(new_text)
            md5 = hashlib.md5(to_bytes(source_url)).hexdigest()
            app_item, flag = YYModel.objects.get_or_create(
                md5=md5,
                defaults={
                    "title": title,
                    'url': source_url,
                    'md5': md5
                }
            )
            if flag:
                item = YYModelMeta(app_item)
                new_type = []
                for url, text in zip(urls, texts):
                    new_type.append((url, text))
                item["urls"] = new_type
                yield item
