# -*- encoding: utf-8 -*-
import os, hashlib
import logging
import scrapy
import time
from scrapy.exceptions import DropItem, NotConfigured
from scrapy.http import Request
from scrapy.utils.python import to_bytes
from .base_download import AbstractFileDownloadPipeline
from ..shentong_baidu_spider import BossSpider


class VideoDownloadPipeline(AbstractFileDownloadPipeline):

    def get_media_requests(self, item, info):
        source_url = item.get("url")
        name = item.get("name")
        yield scrapy.Request(
            url=source_url,
            dont_filter=True,
            meta={"name": name, "is_render": 0}
        )

    def item_completed(self, results, item, info):
        file_infos = [x for ok, x in results if ok]
        if not file_infos:
            raise Exception("File downloads fail")
        logging.getLogger(__name__).info("video download complete")
        with open(os.path.join(BossSpider.custom_settings.get("FILES_STORE"), item.get("name")), "rb") as f:
            md5 = self.get_file_md5(f)
            md5_name = str(md5) + "." + item.get("name").split(".")[-1]
            md5_path = os.path.join(BossSpider.custom_settings.get("SOURCE_STORE"), md5_name)
            if not os.path.exists(md5_name):
                open(md5_path, "wb+").write(
                    open(os.path.join(BossSpider.custom_settings.get("FILES_STORE"), item.get("name")), "rb").read())
        return item

    def file_path(self, request, response=None, info=None) -> str:
        file_name = response.meta.get("name")
        filepath = []
        filepath.append(file_name)
        return os.path.join(*filepath)

    def get_file_md5(self, f):
        m = hashlib.md5()
        while True:
            # 如果不用二进制打开文件，则需要先编码
            # data = f.read(1024).encode('utf-8')
            data = f.read(1024)  # 将文件分块读取
            if not data:
                break
            m.update(data)
        return m.hexdigest()
