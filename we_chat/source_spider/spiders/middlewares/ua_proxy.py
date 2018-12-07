# -*- encoding: utf-8 -*-

import random
from scrapy.downloadermiddlewares.useragent import UserAgentMiddleware
from fake_useragent import UserAgent

class RandomUserAgent(UserAgentMiddleware):
    def __init__(self, user_agent='Scrapy'):
        self.user_agent = user_agent
        self.ua_obj = UserAgent()
    def process_request(self, request, spider):
        ua = self.ua_obj.random
        if ua:
            request.headers.setdefault('User-Agent', ua)