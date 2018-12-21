from source_spider.spiders.utils import DjangoItem
from django.db import models
import django.utils.timezone as timezone
import scrapy


class YYModel(models.Model):
    title = models.CharField(max_length=2048)
    url = models.URLField(max_length=2048)
    md5 = models.CharField(max_length=64, unique=True)
    path = models.CharField(max_length=2048)
    create_time = models.DateTimeField(default=timezone.now)
    update_time = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "yy_source"


class YYModelMeta(DjangoItem):
    django_model = YYModel
    urls = scrapy.Field()
