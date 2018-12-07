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
from source_spider.spiders.models import MovieModel
from ..utils.url_type import parse_url_type


class MovieSpider(scrapy.Spider):
    """
    阳光电影爬虫
    """
    name = "ygdy_spider"

    custom_settings = {
        "DOWNLOAD_DELAY": 1,
        "RETRY_TIMES": 1,
        "DEPTH_LIMIT": 90,
        "ROUNTINE_INTERVAL": 60 * 60 * 24,
        "CONCURRENT_REQUESTS": 32,
        "DOWNLOAD_TIMEOUT": 20,
        "MEDIA_ALLOW_REDIRECTS": True,
        "DOWNLOADER_MIDDLEWARES": {
            'source_spider.spiders.middlewares.RandomUserAgent': 501,
            'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
        },
        "SPIDER_MIDDLEWARES": {
            'source_spider.spiders.middlewares.RoutineSpiderMiddleware': 543,
            'scrapy.spidermiddlewares.depth.DepthMiddleware': 900,
        },
    }

    def __init__(self, *args, **kwargs):
        super(MovieSpider, self).__init__(*args, **kwargs)
        self.start_url = "http://www.ygdy8.net/index.html"

    def start_requests(self):
        yield scrapy.Request(
            url=self.start_url, callback=self.parse_index, dont_filter=True,
        )

    def parse_index(self, response):
        url = response.url
        parents_node = response.xpath('(//div[@id="menu"]/div[@class="contain"]/ul/li/a)[position()<13]')
        for sub_node in parents_node:
            cate = sub_node.xpath("./text()").extract_first()
            sub_url = sub_node.xpath("./@href").extract_first()
            if cate and sub_url:
                sub_url = urlparse.urljoin(url, sub_url)
                yield scrapy.Request(url=sub_url, meta={"cate": cate}, callback=self.dispath_page)

    def dispath_page(self, response):
        url = response.url
        cate = response.meta.get("cate")
        total_string = response.xpath('//div[@class="co_content8"]/div[@class="x"]/text()')
        if total_string:
            total_string = total_string.strip()
            pattern = re.compile(r"共(\d+)页")
            result = re.search(pattern, total_string)
            total_number = result.group(1)
            if total_number:
                total_number = int(total_number)
                for i in range(1, total_number + 1):
                    new_url = re.sub(pattern, "page=" + str(i), url)
                    yield scrapy.Request(url=new_url, callback=self.parse_list, meta={"cate": cate})

    def parse_list(self, response):
        url = response.url
        cate = response.meta.get("cate")
        node_list = response.xpath('//div[@class="movielist"]/ul/li/h5/a')
        for node in node_list:
            detail_url = node.xpath("./@href").extract_first()
            title = node.xpath("./text()").extract_first()
            detail_url = urlparse.urljoin(url, detail_url)
            yield scrapy.Request(url=detail_url, meta={"cate": cate, 'title': title}, callback=self.parse_detail)

    def parse_detail(self, response):
        cate = response.meta.get("cate")
        title = response.meta.get("title")
        year = response.xpath('(//div[@class="info"]/ul/li)[1]/text()[1]').extract_first()
        url = response.xpath('//input[@class="down_url"]/@value').extract_first()
        if url:
            url = url.strip()
            md5 = hashlib.md5(to_bytes(url)).hexdigest()
            url_cate = parse_url_type(url)
            app_item, flag = MovieModel.objects.get_or_create(
                md5=md5,
                defaults={
                    "title": title,
                    'url': url,
                    'md5': md5,
                    'movie_cate': cate,
                    'url_cate': url_cate,
                    'year': year
                }
            )
            print(flag)
