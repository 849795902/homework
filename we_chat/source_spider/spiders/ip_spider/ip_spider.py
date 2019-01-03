# -*- coding: utf-8 -*-

import scrapy
import lxml
# todo:处理特殊字符
import emoji
import os
import re, json, random, logging
import urllib, hashlib
from scrapy.utils.python import to_bytes
from .models import IPModel
import redis
from scrapy.utils.project import get_project_settings
from bs4 import BeautifulSoup


class IpSpider(scrapy.Spider):
    """
    IP爬虫
    """
    name = "ip_spider"

    custom_settings = {
        "IP_LIMIT": 400,
        "DOWNLOAD_DELAY": 0.5,
        "RETRY_TIMES": 1,
        "DEPTH_LIMIT": 90,
        "ROUNTINE_INTERVAL": 60 * 15,
        "CONCURRENT_REQUESTS": 5,
        "DOWNLOAD_TIMEOUT": 20,
        "MEDIA_ALLOW_REDIRECTS": True,
        "DOWNLOADER_MIDDLEWARES": {
            # 'source_spider.spiders.middlewares.RandomUserAgent': 501,
            # 'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
            "source_spider.spiders.middlewares.SeleniumMiddleware": 503,
            'source_spider.spiders.middlewares.AddRefer': 510
        },
        "SPIDER_MIDDLEWARES": {
            'source_spider.spiders.middlewares.RoutineSpiderMiddleware': 543,
            'scrapy.spidermiddlewares.depth.DepthMiddleware': 900,
        },
    }
    settings = get_project_settings()
    redis_host = settings.get("REDISHOST")
    redis_port = settings.get("REDISPORT")
    redis_passwd = settings.get("REDISPASSWORD")

    def __init__(self, *args, **kwargs):
        super(IpSpider, self).__init__(*args, **kwargs)
        # cate = kwargs.get("cate")
        self.start_url = {"goubanjia": ["http://www.goubanjia.com/"],
                          "xici": ['http://www.xicidaili.com/nn/{}'.format(page) for page in range(1, 3)]}

    def start_requests(self):
        count = len(IPModel.objects.all())
        if count < self.settings.get("IP_LIMIT"):
            for ip_site, url_list in self.start_url.items():
                for url in url_list:
                    if ip_site == "goubanjia":
                        yield scrapy.Request(url=url, callback=self.parse_index)
                    elif ip_site == "xici":
                        yield scrapy.Request(url=url, callback=self.parse_xici_index)

    def parse_xici_index(self,response):
        data=response.text
        soup = BeautifulSoup(data, 'html.parser')
        trs1 = soup.find('table', id='ip_list')
        print(data)
        if trs1:
            trs = trs1.find_all('tr')
            for tr in trs[1:]:
                tds = tr.find_all('td')
                if tds[1].find('img') is None:
                    nation = '未知'
                    locate = '未知'
                else:
                    nation = tds[1].find('img')['alt'].strip()
                    locate = tds[4].text.strip()
                ip = tds[1].text.strip()
                port = tds[2].text.strip()
                address = "中国 " + tds[3].text.strip()
                anony = tds[4].text.strip()
                protocol = tds[5].text.strip()
                if ip:
                    md5 = hashlib.md5(bytes(ip, encoding="utf-8")).hexdigest()
                    app_item, flag = IPModel.objects.get_or_create(
                        md5=md5,
                        defaults={
                            "ip": ip + ":" + port,
                            "nimingdu": anony,
                            "type": protocol,
                            "guishudi": address,
                        }
                    )
                    if flag:
                        logging.getLogger(__name__).info(f"save item ip:{ip} guishudi:{address}")

    def parse_index(self, response):
        parents_html = response.xpath(
            '//table[contains(@class,"table")]/tbody/tr')
        for item_obj in parents_html:
            item_list = item_obj.xpath(".//td[@class='ip']/*")
            ip_list = list()
            for item in item_list:
                flag = item.xpath("./@style").extract_first()
                if flag is None or flag.replace(" ", "") != "display:none;":
                    ip_temp = item.xpath(".//text()").extract_first()
                    if ip_temp:
                        ip_list.append(ip_temp)
            ip = "".join(ip_list[0:-1])
            port = item_obj.xpath(".//td[@class='ip']/*[contains(@class,'port')]/text()").extract_first()
            ip = ip + ":" + port
            nimingdu = item_obj.xpath(".//td[2]//text()").extract_first()
            type = item_obj.xpath(".//td[3]//text()").extract_first()
            guishudi = item_obj.xpath(".//td[4]//text()").extract()
            guishudi = [temp.replace(" ", "") for temp in guishudi]
            guishudi = ''.join(guishudi)
            if ip:
                md5 = hashlib.md5(to_bytes(ip)).hexdigest()
                app_item, flag = IPModel.objects.get_or_create(
                    md5=md5,
                    defaults={
                        "ip": ip,
                        "nimingdu": nimingdu,
                        "type": type,
                        "guishudi": guishudi,
                    }
                )
                if flag:
                    logging.getLogger(__name__).info(f"save item ip:{ip} guishudi:{guishudi}")
        self.save_redis_ip()

    def save_redis_ip(self):
        redis_conn = redis.Redis(host=self.redis_host, port=self.redis_port, db=0, password=self.redis_passwd)
        redis_ip_list = redis_conn.hgetall("useful_proxy")
        for ip, _ in redis_ip_list.items():
            ip = ip.decode("utf-8")
            md5 = hashlib.md5(to_bytes(ip)).hexdigest()
            guishudi = "中国"
            nimingdu = "普通"
            app_item, flag = IPModel.objects.get_or_create(
                md5=md5,
                defaults={
                    "ip": ip,
                    "type": "http",
                    "nimingdu": nimingdu,
                    "guishudi": guishudi,
                }
            )
            if flag:
                logging.getLogger(__name__).info(f"save item ip:{ip} guishudi:{guishudi}")
