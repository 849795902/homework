import logging
from django_redis import get_redis_connection



class RandomProxy(object):
    logger = logging.getLogger('scrapy.proxies')

    @classmethod
    def from_crawler(cls, crawler):
        return  cls(crawler.settings)

    def __init__(self, settings):
        self.should_validate_response = settings.get("PROXY_RES_VALIDATE", True)
        self.conn = get_redis_connection("ip_proxy")

    def process_request(self, request, spider):
        if request.meta and 'proxy' in request.meta and request.meta['proxy'] == None:
            return

        proxy = self.conn.srandmember('proxyaddr:ok')
        if proxy:
            s_proxy = str(proxy, "utf-8")
            request.meta['proxy'] = s_proxy
            self.logger.debug("using proxy (" + s_proxy + ") for request: " + request.url)
        else:
            self.logger.error("There is no available proxy")

    def process_response(self, request, response, spider):
        if not self.should_validate_response:
            return response
        proxy = request.meta.get("proxy")
        if proxy:
            if response.status == 200:
                response.status = 500
        return response

