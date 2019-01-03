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
from .models import BossModel
from ..utils.url_type import parse_url_type


class BossSpider(scrapy.Spider):
    """
    lagou爬虫
    """
    name = "boss_spider"

    custom_settings = {
        "DOWNLOAD_DELAY": 2,
        "RETRY_TIMES": 5,
        "DEPTH_LIMIT": 90,
        # "ROUNTINE_INTERVAL": 0,
        "CONCURRENT_REQUESTS": 32,
        "DOWNLOAD_TIMEOUT": 20,
        "MEDIA_ALLOW_REDIRECTS": True,
        "REDIRECT_ENABLED": False,
        "DOWNLOADER_MIDDLEWARES": {
            'source_spider.spiders.middlewares.RandomUserAgent': 501,
            'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
            # "source_spider.spiders.middlewares.SeleniumMiddleware": 503
            'source_spider.spiders.middlewares.RandomProxy': 531,
            'source_spider.spiders.middlewares.ProcessAllExceptionMiddleware': 540
        },
        "SPIDER_MIDDLEWARES": {
            # 'source_spider.spiders.middlewares.RoutineSpiderMiddleware': 543,
            'scrapy.spidermiddlewares.depth.DepthMiddleware': 900,
        },
    }

    def __init__(self, *args, **kwargs):
        super(BossSpider, self).__init__(*args, **kwargs)
        self.start_url = "https://www.zhipin.com/gongsi/?page=1&ka=page-1"

    def start_requests(self):
        yield scrapy.Request(
            url=self.start_url, callback=self.parse_index, dont_filter=True, meta={"page": 1}
        )

    def parse_index(self, response):
        url = response.url
        page = response.meta.get("page")
        if response.status == 302:
            time.sleep(10 * 60)
            yield scrapy.Request(
                url=url, callback=self.parse_index, dont_filter=True, meta={"page": page}
            )
        parents_node = response.xpath(
            "//div[contains(@class,'company-list')]/ul/li//a[contains(@ka,'brand_list_company')]")
        for sub_node in parents_node:
            company_name = sub_node.xpath(".//h4/text()").extract_first()
            sub_url = sub_node.xpath("./@href").extract_first()
            sub_url = urlparse.urljoin(url, sub_url).replace("gongsi", "gongsir") + "?page=1&ka=page-1"
            yield scrapy.Request(url=sub_url, meta={"company_name": company_name, 'page': 1},
                                 callback=self.parse_company)
        if len(parents_node) > 0:
            page = page + 1
            url = url.split("?")[0] + f"?page={page}&ka=page-{page}"
            yield scrapy.Request(
                url=url, callback=self.parse_index, dont_filter=True, meta={"page": page}
            )

    def parse_company(self, response):
        url = response.url

        company_name = response.meta.get("company_name")
        if response.status == 302:
            time.sleep(10 * 60)
            yield scrapy.Request(url=url, meta={"company_name": company_name, 'page': page},
                                 callback=self.parse_company)
        page = response.meta.get("page")
        parent_node = response.xpath('//div[@class="job-list"]/ul/li/a')
        for item_node in parent_node:
            sub_url = item_node.xpath("./@href").extract_first()
            sub_url = urlparse.urljoin(url, sub_url)
            yield scrapy.Request(url=sub_url, meta={"company_name": company_name}, callback=self.parse_job)
        if len(parent_node) > 0 and page <= 30:
            page = page + 1
            url = url.split("?")[0] + f"?page={page}&ka=page-{page}"
            yield scrapy.Request(url=url, meta={"company_name": company_name, 'page': page},
                                 callback=self.parse_company)

    def parse_job(self, response):
        url = response.url
        company = response.meta.get("company_name")
        if response.status == 302:
            time.sleep(10 * 60)
            yield scrapy.Request(url=url, meta={"company_name": company}, callback=self.parse_job)
        title = response.xpath('//div[contains(@class,"job-primary")]//div[@class="name"]/h1/text()').extract_first()
        wage = response.xpath(
            '//div[contains(@class,"job-primary")]//div[@class="name"]//span[@class="badge"]/text()').extract_first()
        md5 = hashlib.md5(to_bytes(url)).hexdigest()
        city_soon = response.xpath(
            '//div[contains(@class,"job-primary")]//div[@class="info-primary"]/p//text()').extract()
        describe = response.xpath(
            '(//div[contains(@class,"detail-content")]/div[@class="job-sec"])[1]/div[@class="text"]/text()').extract()
        describe = ''.join(describe)
        city = experience = education = None
        for item in city_soon:
            if item.startswith("城市"):
                city = item.split('：')[-1]
            elif item.startswith("经验"):
                experience = item.split("：")[-1]
            elif item.startswith("学历"):
                education = item.split("：")[-1]
        if title:
            wage = wage.strip()
            boss_item, flag = BossModel.objects.get_or_create(
                md5=md5,
                defaults={
                    "title": title,
                    "wage": wage,
                    "md5": md5,
                    "url": url,
                    "company": company,
                    "city": city,
                    "experience": experience,
                    "education": education,
                    "describe": self.parse_html(describe),
                }
            )
            print({
                    "title": title,
                    "company": company,
                    "desc": self.parse_html(describe),
                })
            if flag:
                logging.getLogger(__name__).info(f"save movie title:{title} url:{url}")

    def parse_html(self, html_string):
        trans_str_mapping = {
            "&quot;": "\"",
            "&amp;": "&",
            "&lt;": "<",
            "&gt;": ">",
            "&nbsp;": " ",
            "&ldquo;": "“",
            "&rdquo;": "”",
            "&mdash;": "——"
        }
        pattern_style = re.compile(r'<style.*?>.*?</style>', re.S)
        html_string = re.sub(pattern_style, '', html_string)
        pattern_script = re.compile(r'<script.*?>.*?</script>', re.S)
        html_string = re.sub(pattern_script, '', html_string)
        html_string = re.sub(r'</?\w+[^>]*>', '', html_string)
        pattern_comment = re.compile(r'<!.*?>', re.S)
        html_string = re.sub(pattern_comment, "", html_string)
        html_string = html_string.strip()
        for key, value in trans_str_mapping.items():
            html_string = html_string.replace(key, value)
        return html_string
