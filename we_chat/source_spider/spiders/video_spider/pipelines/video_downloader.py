# -*- encoding: utf-8 -*-
import os, hashlib
import logging
import scrapy

from scrapy.exceptions import DropItem, NotConfigured
from scrapy.http import Request
from scrapy.utils.python import to_bytes
from .base_download import AbstractFileDownloadPipeline


class VideoDownloadPipeline(AbstractFileDownloadPipeline):

    def get_media_requests(self, item, info):
        source_urls = item.get("urls")
        for source_url, source_text in source_urls:
            yield scrapy.Request(
                url=source_url,
                dont_filter=True,
                meta={"item": item, "source_text": source_text}
            )

    def item_completed(self, results, item, info):
        file_infos = [x for ok, x in results if ok]
        if not file_infos:
            raise Exception("File downloads fail")
        logging.getLogger(__name__).info("video download complete")
        item['path'] = os.path.join(self.store.basedir, item.get("title"))
        item.save()
        return item

    def file_path(self, request, response=None, info=None) -> str:
        item = request.meta.get('item')
        title = item.get('title')
        source_text = response.meta.get("source_text")
        dir_name = title
        file_name = source_text + ".ts"
        filepath = []
        filepath.append(dir_name)
        filepath.append(file_name)
        return os.path.join(*filepath)
