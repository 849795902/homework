import logging
import requests


class RandomProxy(object):
    logger = logging.getLogger('scrapy.proxies')

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings)

    def __init__(self, settings):
        self.url = settings.get("PROXY_URL")

    def process_request(self, request, spider):
        if request.meta and 'proxy' in request.meta and request.meta['proxy'] == None:
            return
        response = requests.get(url=self.url)
        proxy = response.text
        if proxy:
            request.meta['proxy'] = proxy
            self.logger.debug("using proxy (" + proxy + ") for request: " + request.url)
        else:
            self.logger.error("There is no available proxy")

