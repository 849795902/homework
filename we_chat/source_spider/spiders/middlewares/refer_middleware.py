# -*- encoding: utf-8 -*-


class AddRefer(object):
    def process_request(self, request, spider):
        rf = request.meta.get("referer")
        if rf:
            request.headers.setdefault('referer', rf)
