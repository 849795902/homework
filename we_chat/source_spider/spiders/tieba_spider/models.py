from source_spider.spiders.utils import DjangoItem
from django.db import models
import django.utils.timezone as timezone


class TieBaModel(models.Model):
    title = models.CharField(max_length=2048)
    url = models.URLField(max_length=2048)
    author = models.CharField(max_length=128)
    md5 = models.CharField(max_length=64, unique=True)
    content = models.TextField()
    create_time = models.DateTimeField(default=timezone.now)
    update_time = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "test_source"


class AppModelMeta(DjangoItem):
    django_model = TieBaModel
