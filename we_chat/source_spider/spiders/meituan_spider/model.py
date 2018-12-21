

from source_spider.spiders.utils import DjangoItem
from django.db import models
import django.utils.timezone as timezone


class ShopModel(models.Model):
    title = models.CharField(max_length=2048)
    addr = models.CharField(max_length=2048)
    url = models.CharField(max_length=20)
    md5 = models.CharField(max_length=64, unique=True)
    cai_name=models.CharField(max_length=2048)
    create_time = models.DateTimeField(default=timezone.now)
    update_time = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "shop_source"


class AppModelMeta(DjangoItem):
    django_model = ShopModel



