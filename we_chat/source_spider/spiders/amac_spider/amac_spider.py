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
from source_spider.spiders.amac_spider.model import AmacModel
from ..utils.url_type import parse_url_type


class AmacSpider(scrapy.Spider):
    """
    amac爬虫
    """
    name = "amac_spider"

    custom_settings = {
        "DOWNLOAD_DELAY": 0,
        "RETRY_TIMES": 1,
        "DEPTH_LIMIT": 90,
        "CONCURRENT_REQUESTS": 10000,
        "DOWNLOAD_TIMEOUT": 5,
        "MEDIA_ALLOW_REDIRECTS": True,
        "DOWNLOADER_MIDDLEWARES": {
            'source_spider.spiders.middlewares.RandomUserAgent': 501,
            'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
        },
        "SPIDER_MIDDLEWARES": {
            'scrapy.spidermiddlewares.depth.DepthMiddleware': 900,
        },
    }

    def __init__(self, *args, **kwargs):
        super(AmacSpider, self).__init__(*args, **kwargs)
        self.start_url = ["http://guba.eastmoney.com/remenba.aspx?type=1&tab={}".format(i) for i in range(1, 7)]

    def start_requests(self):
        for url in self.start_url:
            yield scrapy.Request(
                url=url, callback=self.parse_index, dont_filter=True,
            )

    def parse_index(self, response):
        url = response.url
        parents_node = response.xpath('//div[contains(@class,"ngbggulbody")]//ul/li/a')
        for sub_node in parents_node:
            name = sub_node.xpath("./text()").extract_first()
            sub_url = sub_node.xpath("./@href").extract_first().replace("topic", 'list')
            sub_url = urlparse.urljoin(url, sub_url)
            yield scrapy.Request(url=sub_url, meta={"name": name}, callback=self.parse_list)

    def parse_list(self, response):
        url = response.url
        name = response.meta.get("name")
        node_list = response.xpath('//div[@id="articlelistnew"]/div[contains(@class,"articleh")]')
        page_num_str = response.xpath('//span[@class="pagernums"]/@data-pager').extract_first()
        if page_num_str:
            page_num_list = page_num_str.split("|")
            page_num = int(int(page_num_list[1]) / int(page_num_list[2]))
            for node in node_list:
                detail_url = node.xpath(".//span[@class='l3']/a/@href").extract_first()
                title = node.xpath(".//span[@class='l3']/a/text()").extract_first()
                author=node.xpath(".//span[@class='l4']//text()").extract_first()
                detail_url = urlparse.urljoin(url, detail_url)
                publish_time = node.xpath(".//span[@class='l5']/text()").extract_first()
                if all((detail_url, title, publish_time)):
                    item = {"detail_url": detail_url, "title": title, 'publish_time': publish_time, 'name': name,'author':author}
                    yield scrapy.Request(url=detail_url, meta={"item": item}, callback=self.parse_detail)
            # page_num=1
            for num in range(2, page_num + 1):
                if "_" in url:
                    url = url.split("_")[0] + '_' + str(num) + '.html'
                else:
                    url = url.replace(".html", '_' + str(num) + '.html')
                yield scrapy.Request(url=url, meta={"name": name},
                                     callback=self.parse_list)

    def parse_detail(self, response):
        item = response.meta.get("item")
        content = response.xpath('//div[@id="post_content"]').extract_first()
        if content:
            url = item.get("detail_url").strip()
            md5 = hashlib.md5(to_bytes(url)).hexdigest()
            title = item.get("title")
            author=item.get("author")
            publish_time=item.get("publish_time")
            parent_name = item.get("name")
            app_item, flag = AmacModel.objects.get_or_create(
                md5=md5,
                defaults={
                    "title": title,
                    'url': url,
                    'md5': md5,
                    'parent_name': parent_name,
                    'content': content,
                    'author':author,
                    'publish_time':publish_time
                }
            )
            if flag:
                logging.getLogger(__name__).info(f"save amac title:{title} url:{url}")
