from source_spider.spiders.utils import DjangoItem
from django.db import models
import django.utils.timezone as timezone


class AmacModel(models.Model):
    parent_name = models.CharField(max_length=2048)
    url = models.URLField(max_length=2048)
    title=models.CharField(max_length=2048)
    content = models.TextField()
    author=models.CharField(max_length=2048)
    publish_time=models.CharField(max_length=2048)
    md5 = models.CharField(max_length=64, unique=True)
    create_time = models.DateTimeField(default=timezone.now)
    update_time = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "amac_source"


class AppModelMeta(DjangoItem):
    django_model = AmacModel


