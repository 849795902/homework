from source_spider.spiders.utils import DjangoItem
from django.db import models
import django.utils.timezone as timezone


class IPModel(models.Model):
    ip = models.CharField(max_length=2048)
    nimingdu = models.CharField(max_length=2048)
    type = models.CharField(max_length=128)
    md5 = models.CharField(max_length=64, unique=True)
    guishudi = models.CharField(max_length=1024)
    create_time = models.DateTimeField(default=timezone.now)
    update_time = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "ip_source"


class AppModelMeta(DjangoItem):
    django_model = IPModel
