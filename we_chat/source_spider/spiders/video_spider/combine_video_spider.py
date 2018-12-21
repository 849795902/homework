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
    name = "yy_combine_spider"

    custom_settings = {
        "FILES_STORE": "video",
        "DOWNLOAD_DELAY": 0,
        "RETRY_TIMES": 1,
        "CONCURRENT_REQUESTS": 32,
        "DOWNLOAD_TIMEOUT": 20,
        "MEDIA_ALLOW_REDIRECTS": True,
        "DOWNLOADER_MIDDLEWARES": {
            'source_spider.spiders.middlewares.RandomUserAgent': 501,
            'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
        },
    }

    def __init__(self, *args, **kwargs):
        super(MovieSpider, self).__init__(*args, **kwargs)
        self.start_url = "http://www.baidu.com.cn"

    def start_requests(self):
        yield scrapy.Request(
            url=self.start_url, callback=self.parse_index, dont_filter=True,
        )

    def parse_index(self, response):
        obj_list = YYModel.objects.all()
        for item in obj_list:
            path = item.path
            if path:
                if not path.startswith("F:"):
                    path = "F:/" + path
                path = path.replace("\\", "/")
                path_list = path.split("/")[0:3]
                fin_path = path.split("/")[0:2]
                path = "/".join(path_list)
                path = path.replace(".ts", "")
                fin_path = '/'.join(fin_path)
                title = item.title
                exec_str = r'copy /b  "' + path + r'\*.ts" "' + fin_path + '/' + title + '.ts"'
                print(exec_str)
                os.system(exec_str)
                exec_str = r'del  "' + path + r'\*.ts"'
                print(exec_str)
                os.system(exec_str)
                item.path = fin_path + "/" + title + '.ts'
                item.save()
