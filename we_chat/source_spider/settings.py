# -*- coding: utf-8 -*-
import os

BOT_NAME = 'source_spider'

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SPIDER_MODULES = ['source_spider.spiders']
NEWSPIDER_MODULE = 'source_spider.spiders'

# Crawl responsibly by identifying yourself (and your website) on the user-agent
# USER_AGENT = 'source_spider (+http://www.yourdomain.com)'

LOG_LEVEL = 'DEBUG'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

SELENIUM_TIMEOUT = 20
if os.path.exists("/root/env"):
    CHROME_DRIVER_PATH = "/usr/bin/chromedriver"
else:
    CHROME_DRIVER_PATH = "C:\Python\Python36\Scripts\chromedriver.exe"

SPLASH_URL = 'http://188.131.195.22:8050/'

REDISHOST = "188.131.195.22"
REDISPORT = 6379
REDISPASSWORD = "!@#abcABC123"

PROXY_URL = "http://188.131.195.22:8000/django_api/get_proxy/"

ELS_URI = "188.131.195.22"
ELS_DB = "spider"

# Configure maximum concurrent requests performed by Scrapy (default: 16)
# CONCURRENT_REQUESTS = 32

# Configure a delay for requests for the same website (default: 0)
# See https://doc.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
# DOWNLOAD_DELAY = 3
# The download delay setting will honor only one of:
# CONCURRENT_REQUESTS_PER_DOMAIN = 16
# CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
# COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
# TELNETCONSOLE_ENABLED = False

# Override the default request headers:
# DEFAULT_REQUEST_HEADERS = {
#   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#   'Accept-Language': 'en',
# }

# Enable or disable spider middlewares
# See https://doc.scrapy.org/en/latest/topics/spider-middleware.html
# SPIDER_MIDDLEWARES = {
#    'source_spider.middlewares.SourceSpiderSpiderMiddleware': 543,
# }

# Enable or disable downloader middlewares
# See https://doc.scrapy.org/en/latest/topics/downloader-middleware.html
# DOWNLOADER_MIDDLEWARES = {
#    'source_spider.middlewares.SourceSpiderDownloaderMiddleware': 543,
# }

# Enable or disable extensions
# See https://doc.scrapy.org/en/latest/topics/extensions.html
# EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
# }

# Configure item pipelines
# See https://doc.scrapy.org/en/latest/topics/item-pipeline.html
# ITEM_PIPELINES = {
#    'source_spider.pipelines.SourceSpiderPipeline': 300,
# }

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://doc.scrapy.org/en/latest/topics/autothrottle.html
# AUTOTHROTTLE_ENABLED = True
# The initial download delay
# AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
# AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
# AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
# AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://doc.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
# HTTPCACHE_ENABLED = True
# HTTPCACHE_EXPIRATION_SECS = 0
# HTTPCACHE_DIR = 'httpcache'
# HTTPCACHE_IGNORE_HTTP_CODES = []
# HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'
# django orm setup
import os
import django

os.environ['DJANGO_SETTINGS_MODULE'] = 'source_spider.django_settings'
django.setup()
