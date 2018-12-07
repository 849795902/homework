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
from source_spider.spiders.models import AppModelMeta, AppModel
from ..utils.url_type import parse_url_type


class AppSpider(scrapy.Spider):
    """
    2345app爬虫
    """
    name = "2345app_spider"

    custom_settings = {
        "DOWNLOAD_DELAY": 2,
        "RETRY_TIMES": 5,
        "DEPTH_LIMIT": 90,
        "ROUNTINE_INTERVAL": 60 * 60 * 24 * 24,
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
        super(AppSpider, self).__init__(*args, **kwargs)
        self.start_url = "http://www.duote.com/sort.html"

    def start_requests(self):
        yield scrapy.Request(
            url=self.start_url, callback=self.parse_index, dont_filter=True,
        )

    def parse_index(self, response):
        url = response.url
        parents_node = response.xpath('(//div[@class="raider-content"])[2]/a[position()>1]')
        for sub_node in parents_node:
            cate = sub_node.xpath("./text()").extract_first()
            sub_url = sub_node.xpath("./@href").extract_first()
            sub_url = urlparse.urljoin(url, sub_url)
            yield scrapy.Request(url=sub_url, meta={"cate": cate}, callback=self.dispath_page)

    def dispath_page(self, response):
        append_str = "{}_.html"
        url = response.url[:-7]
        cate = response.meta.get("cate")
        total_number = response.xpath('//a[@title="下一页"]/preceding-sibling::a[1]/text()').extract_first().strip()
        if total_number:
            total_number = int(total_number)
            for i in range(1, total_number + 1):
                new_url = url + append_str.format(i)
                yield scrapy.Request(url=new_url, callback=self.parse_list, meta={"cate": cate})

    def parse_list(self, response):
        url = response.url
        cate = response.meta.get("cate")
        node_list = response.xpath('//div[@class="soft-info-lists"]/div[@class="soft-info-list"]/a')
        for node in node_list:
            detail_url = node.xpath("./@href").extract_first()
            detail_url = urlparse.urljoin(url, detail_url)
            yield scrapy.Request(url=detail_url, meta={"cate": cate}, callback=self.parse_detail)

    def parse_detail(self, response):
        cate = response.meta.get("cate")
        title = response.xpath('//div[@class="soft-name"]/div[@class="max_widths"]/text()').extract_first().strip()
        url = response.xpath('//div[@class="download-box"][last()]/a[@class="down-list"]/@href').extract_first()
        if url:
            url = url.strip()
            md5 = hashlib.md5(to_bytes(url)).hexdigest()
            url_cate = parse_url_type(url)
            app_item, flag = AppModel.objects.get_or_create(
                md5=md5,
                defaults={
                    "title": title,
                    'url': url,
                    'md5': md5,
                    'app_cate': cate,
                    'url_cate': url_cate
                }
            )
            if flag:
                logging.getLogger(__name__).info(f"save app title:{title} url:{url}")

