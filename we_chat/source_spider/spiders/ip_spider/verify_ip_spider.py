# -*- coding: utf-8 -*-

import scrapy
import redis
import lxml
# todo:处理特殊字符
import emoji
import os
import re, json, random, logging
import urllib, hashlib
from scrapy.utils.python import to_bytes
from .models import IPModel
import requests
from scrapy.utils.project import get_project_settings


class IpSpider(scrapy.Spider):
    """
    verify_IP爬虫
    """
    name = "verify_ip_spider"

    custom_settings = {
        "DOWNLOAD_DELAY": 0.5,
        "DEPTH_LIMIT": 90,
        "ROUNTINE_INTERVAL": 60 * 15,
        "DOWNLOAD_TIMEOUT": 10,
        "SPIDER_MIDDLEWARES": {
            'source_spider.spiders.middlewares.RoutineSpiderMiddleware': 543,
        },
    }
    settings = get_project_settings()
    redis_host = settings.get("REDISHOST")
    redis_port = settings.get("REDISPORT")
    redis_passwd = settings.get("REDISPASSWORD")

    def __init__(self, *args, **kwargs):
        super(IpSpider, self).__init__(*args, **kwargs)
        # cate = kwargs.get("cate")
        self.start_nation_url = "https://www.baidu.com/"
        self.start_foreign_url = "https://www.google.com.hk/"

    def start_requests(self):
        ip_list = IPModel.objects.all()
        for ip_obj in ip_list:
            ip = ip_obj.ip
            ip_type = ip_obj.type
            guishudi = ip_obj.guishudi
            guishudi = guishudi.strip() if guishudi else "中国"
            ip_type = ip_type.strip() if ip_type else "http"
            url = self.start_nation_url if guishudi.startswith("中国") else self.start_foreign_url
            headers = {
                'user-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.67 Safari/537.36'}
            try:
                proxies = {
                    ip_type: ip_type + "://" + ip,
                }
                result = requests.get(url=url, proxies=proxies, timeout=self.custom_settings.get("DOWNLOAD_TIMEOUT"),
                                      headers=headers)
            except Exception as e:
                logging.getLogger(__name__).info(f"delete proxy ip {ip}")
                ip_obj.delete()
                self.delete_redis_ip(ip)

            else:
                if result.status_code != 200:
                    logging.getLogger(__name__).info(f"delete proxy ip {ip}")
                    ip_obj.delete()
                    self.delete_redis_ip(ip)
        yield scrapy.Request(url=self.start_nation_url, callback=self.parse)

    def parse(self, response):
        pass

    def delete_redis_ip(self, ip):
        redis_conn = redis.Redis(host=self.redis_host, port=self.redis_port, db=0, password=self.redis_passwd)
        result = redis_conn.hdel("useful_proxy", ip)
        if result:
            logging.getLogger(__name__).info(f"delete redis proxy ip {ip}")
