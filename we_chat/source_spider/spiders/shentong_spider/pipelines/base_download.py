import logging
from collections import defaultdict

from scrapy.pipelines.files import FSFilesStore
from scrapy.utils.datatypes import SequenceExclude
from scrapy.utils.defer import mustbe_deferred, defer_result
from scrapy.utils.log import failure_to_exc_info
from scrapy.utils.misc import md5sum
from scrapy.utils.request import referer_str
from scrapy.utils.request import request_fingerprint
from twisted.internet.defer import Deferred, DeferredList

try:
    from cStringIO import StringIO as BytesIO
except ImportError:
    from io import BytesIO

logger = logging.getLogger("FileDownloadPipeline")


class FileException(Exception):
    """General media error exception"""


class AbstractFileDownloadPipeline(object):
    class SpiderInfo(object):
        def __init__(self, spider):
            self.spider = spider
            self.downloading = set()
            self.waiting = defaultdict(list)

    def __init__(self, crawler):
        super(AbstractFileDownloadPipeline, self).__init__()
        self.crawler = crawler
        base_dir = crawler.settings.get('FILES_STORE')
        if not base_dir:
            raise Exception("FILES_STORE can not find")
        self.store = FSFilesStore(base_dir)

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler)

    def open_spider(self, spider):
        self.spiderinfo = self.SpiderInfo(spider)

    def process_item(self, item, spider):
        info = self.spiderinfo
        if not self.need_process(item):
            self.item_completed([(True, None)], item, info)
        dlist = [self._process_request(r, info) for r in self.get_media_requests(item, info)]
        dfd = DeferredList(dlist, consumeErrors=True)
        return dfd.addBoth(self.item_completed, item, info)

    def _process_request(self, request, info):
        fp = request_fingerprint(request)
        cb = request.callback or (lambda _: _)
        eb = request.errback
        request.callback = None
        request.errback = None

        # Otherwise, wait for result
        wad = Deferred().addCallbacks(cb, eb)
        info.waiting[fp].append(wad)

        # Check if request is downloading right now to avoid doing it twice
        if fp in info.downloading:
            return wad
        # Download request checking media_to_download hook output first
        info.downloading.add(fp)

        dfd = mustbe_deferred(self.media_to_download, request, info)
        dfd.addCallback(self._check_media_to_download, request, info)
        dfd.addBoth(self._execute_waiters, fp, info)
        dfd.addErrback(lambda f: logger.error(
            f.value, exc_info=failure_to_exc_info(f), extra={'spider': info.spider})
                       )
        return dfd.addBoth(lambda _: wad)  # it must return wad at last

    def _check_media_to_download(self, result, request, info):
        if result is not None:
            return result

        request.meta['handle_httpstatus_list'] = SequenceExclude(range(300, 400))
        dfd = self.crawler.engine.download(request, info.spider)
        dfd.addCallbacks(
            callback=self._respback, callbackArgs=(request, info),
            errback=self._errback, errbackArgs=(request, info))
        return dfd

    def _execute_waiters(self, result, fp, info):
        info.downloading.remove(fp)
        for wad in info.waiting.pop(fp):
            defer_result(result).chainDeferred(wad)

    def _inc_stats(self, spider, status):
        spider.crawler.stats.inc_value('file_count', spider=spider)
        spider.crawler.stats.inc_value('file_status_count/%s' % status, spider=spider)

    def _respback(self, response, request, info):
        referer = referer_str(request)

        if response.status != 200:
            logger.warning(
                'File (code: %(status)s): Error downloading file from '
                '%(request)s referred in <%(referer)s>',
                {'status': response.status,
                 'request': request, 'referer': referer},
                extra={'spider': info.spider}
            )
            raise FileException('download-error')

        if not response.body:
            logger.warning(
                'File (empty-content): Empty file from %(request)s referred '
                'in <%(referer)s>: no-content',
                {'request': request, 'referer': referer},
                extra={'spider': info.spider}
            )
            raise FileException('empty-content')

        status = 'cached' if 'cached' in response.flags else 'downloaded'
        logger.debug(
            'File (%(status)s): Downloaded file from %(request)s referred in '
            '<%(referer)s>',
            {'status': status, 'request': request, 'referer': referer},
            extra={'spider': info.spider}
        )
        self._inc_stats(info.spider, status)

        try:
            path = self.file_path(request, response=response, info=info)
            checksum = self.file_downloaded(response, request, info)
        except FileException as exc:
            logger.warning(
                'File (error): Error processing file from %(request)s '
                'referred in <%(referer)s>: %(errormsg)s',
                {'request': request, 'referer': referer, 'errormsg': str(exc)},
                extra={'spider': info.spider}, exc_info=True
            )
            raise
        except Exception as exc:
            logger.error(
                'File (unknown-error): Error processing file from %(request)s '
                'referred in <%(referer)s>',
                {'request': request, 'referer': referer},
                exc_info=True, extra={'spider': info.spider}
            )
            raise FileException(str(exc))

        return {'url': request.url, 'path': path, 'checksum': checksum}

    def _errback(self, failure, request, info):
        """Handler for failed downloads"""
        return failure

    ### Overridable Interface
    def media_to_download(self, request, info):
        """Check request before starting download"""
        pass

    def get_media_requests(self, item, info):
        """Returns the media requests to download"""
        pass

    def file_path(self, request, response=None, info=None):
        raise NotImplementedError()

    def file_downloaded(self, response, request, info):
        path = self.file_path(request, response=response, info=info)

        buf = BytesIO(response.body)
        checksum = md5sum(buf)
        buf.seek(0)
        self.store.persist_file(path, buf, info)
        return checksum

    def item_completed(self, results, item, info):
        return item

    def need_process(self, item):
        return True
