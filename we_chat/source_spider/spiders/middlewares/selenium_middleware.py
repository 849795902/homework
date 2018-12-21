from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from scrapy.http import HtmlResponse
from logging import getLogger


class SeleniumMiddleware(object):
    """
    若添加了该中间件后不需要渲染了，在meta中设置is_render:0
    """
    @classmethod
    def from_crawler(cls, crawler):
        return cls(timeout=crawler.settings.get("SELENIUM_TIMEOUT"), path=crawler.settings.get("CHROME_DRIVER_PATH"))

    def __init__(self, timeout=None, path=None):
        self.logger = getLogger(__name__)
        self.timeout = timeout
        self.path = path
        self.chrome_opt = webdriver.ChromeOptions()
        prefs = {"profile.managed_default_content_settings.images": 2}
        # 将参数设置到chrome_opt里面
        # self.chrome_opt.add_experimental_option("prefs", prefs)
        # self.chrome_opt.add_argument('--headless')
        self.chrome_opt.add_argument('--no-sandbox')
        # 模拟浏览器的时候将chrome_opt添加进去
        self.browser = webdriver.Chrome(executable_path=self.path, chrome_options=self.chrome_opt)

    def __del__(self):
        self.browser.close()

    def process_request(self, request, spider):
        is_render = request.meta.get("is_render")
        if is_render != 0:
            try:
                self.browser.get(request.url)
                self.browser.implicitly_wait(self.timeout)
                body = self.browser.page_source
                return HtmlResponse(url=request.url, body=body, request=request, encoding="utf-8",
                                    status=200)
            except TimeoutException:
                return HtmlResponse(url=request.url, status=500, request=request)
