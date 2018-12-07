from source_spider.spiders.utils import DjangoItem
from django.db import models
import django.utils.timezone as timezone


class AppModel(models.Model):
    title = models.CharField(max_length=2048)
    url = models.URLField(max_length=2048)
    url_cate = models.CharField(max_length=20)
    app_cate = models.CharField(max_length=128)
    md5 = models.CharField(max_length=64, unique=True)
    create_time = models.DateTimeField(default=timezone.now)
    update_time = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "app_source"


class AppModelMeta(DjangoItem):
    django_model = AppModel


class MovieModel(models.Model):
    title = models.CharField(max_length=2048)
    url = models.URLField(max_length=2048)
    url_cate = models.CharField(max_length=20)
    movie_cate = models.CharField(max_length=128)
    md5 = models.CharField(max_length=64, unique=True)
    year = models.CharField(max_length=255)
    create_time = models.DateTimeField(default=timezone.now)
    update_time = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "movie_source"


class MovieModelMeta(DjangoItem):
    django_model = AppModel
