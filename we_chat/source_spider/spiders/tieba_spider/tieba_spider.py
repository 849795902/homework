# -*- coding: utf-8 -*-

import scrapy
import lxml
# todo:处理特殊字符
import emoji
import os
import re, json, random, logging
import urllib, hashlib
import time, datetime
from django.forms import model_to_dict
from urllib import parse as urlparse
from datetime import timedelta
from scrapy.utils.python import to_bytes
from source_spider.spiders.tieba_spider.models import TieBaModel
from ..utils.url_type import parse_url_type


class TiebaSpider(scrapy.Spider):
    """
    iiDVD爬虫
    """
    name = "tieba_spider"

    custom_settings = {
        "DOWNLOAD_DELAY": 0.5,
        "RETRY_TIMES": 1,
        "DEPTH_LIMIT": 90,
        "ROUNTINE_INTERVAL": 60 * 60 * 24 * 2,
        "CONCURRENT_REQUESTS": 32,
        "DOWNLOAD_TIMEOUT": 20,
        "MEDIA_ALLOW_REDIRECTS": True,
        "HTTPERROR_ALLOWED_CODES": [403],
        "DOWNLOADER_MIDDLEWARES": {
            'source_spider.spiders.middlewares.RandomUserAgent': 501,
            'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
            # "source_spider.spiders.middlewares.SeleniumMiddleware": 503,
            'source_spider.spiders.middlewares.AddRefer': 510
        },
        "SPIDER_MIDDLEWARES": {
            'source_spider.spiders.middlewares.RoutineSpiderMiddleware': 543,
            'scrapy.spidermiddlewares.depth.DepthMiddleware': 900,
        },
    }

    def __init__(self, *args, **kwargs):
        super(TiebaSpider, self).__init__(*args, **kwargs)
        cate = kwargs.get("cate")
        self.total_page = int(kwargs.get("total_page", 100))
        self.start_url = "http://tieba.baidu.com/f?kw=图拉丁&ie=utf-8&pn={}"
        if cate:
            self.start_url = self.start_url.replace("图拉丁", cate)

    def start_requests(self):
        self.referer = self.start_url.format(0)
        for i in range(0, self.total_page * 50 + 1, 50):
            yield scrapy.Request(url=self.start_url.format(i), callback=self.parse_index,
                                 meta={"referer": self.referer})

    def parse_index(self, response):
        url = response.url
        # print(response.text)
        parents_html = response.xpath(
            '//code[@id="pagelet_html_frs-list/pagelet/thread_list"]//comment()').extract_first()
        # 使用comment提取注释内容
        if parents_html:
            pattern = re.compile(r"<!--(.*?)-->", re.S)
            parents_html = self.filter_emoji(parents_html)
            result = re.search(pattern, parents_html)
            if result:
                parents_html = result.group(1)
                html_dom = lxml.html.fromstring(parents_html)
                etree_root = html_dom.getroottree()
                parents_node = etree_root.xpath("//div[contains(@class,'threadlist_title')]//a/@href")
                for sub_node in parents_node:
                    sub_url = urlparse.urljoin(url, sub_node)
                    yield scrapy.Request(url=sub_url, callback=self.parse_detail, meta={"refer": url})

    def parse_detail(self, response):
        url = response.url
        title = response.xpath('//div[contains(@class,"core_title")]/h1/text()').extract_first()
        content = response.xpath('(//div[contains(@id,"post_content")])[1]').extract_first()
        author = response.xpath('//div[contains(@class,"louzhubiaoshi")]/@author').extract_first()
        if title:
            url = url.strip()
            md5 = hashlib.md5(to_bytes(url)).hexdigest()
            app_item, flag = TieBaModel.objects.get_or_create(
                md5=md5,
                defaults={
                    "title": self.filter_emoji(title),
                    'url': url,
                    'md5': md5,
                    "content": self.filter_emoji(content),
                    "author": author
                }
            )
            if flag:
                logging.getLogger(__name__).info(f"save item title:{title} url:{url}")

    @staticmethod
    def filter_emoji(desstr, restr=''):
        try:
            co = re.compile(u'[\U00010000-\U0010ffff]')
        except re.error:
            co = re.compile(u'[\uD800-\uDBFF][\uDC00-\uDFFF]')
        return co.sub(restr, desstr)
