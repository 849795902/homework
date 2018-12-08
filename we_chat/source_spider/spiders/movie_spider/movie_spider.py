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
    iiDVD爬虫
    """
    name = "iidvd_spider"

    custom_settings = {
        "DOWNLOAD_DELAY": 0,
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
        },
        "SPIDER_MIDDLEWARES": {
            'source_spider.spiders.middlewares.RoutineSpiderMiddleware': 543,
            'scrapy.spidermiddlewares.depth.DepthMiddleware': 900,
        },
    }

    def __init__(self, *args, **kwargs):
        super(MovieSpider, self).__init__(*args, **kwargs)
        self.start_url = "http://www.iidvd.com/wunsian.asp"

    def start_requests(self):
        yield scrapy.Request(
            url=self.start_url, callback=self.parse_index, dont_filter=True,
        )

    def parse_index(self, response):
        url = response.url
        parents_node = response.xpath('(//div[@class="filter"]/ul/li)[1]/a')
        for sub_node in parents_node:
            cate = sub_node.xpath("./text()").extract_first()
            sub_url = sub_node.xpath("./@href").extract_first()
            sub_url = urlparse.urljoin(url, sub_url)
            yield scrapy.Request(url=sub_url, meta={"cate": cate}, callback=self.dispath_page)

    def dispath_page(self, response):
        url = response.url
        pattern = re.compile(r"page=(\d+)")
        cate = response.meta.get("cate")
        total_number = response.xpath('//div[@id="pages"]/span/text()').extract_first().strip()
        total_number = total_number.split("/")[-1].replace("页", "")
        if total_number:
            total_number = int(total_number)
            for i in range(1, 4):
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
            if flag:
                logging.getLogger(__name__).info(f"save movie title:{title} url:{url}")
