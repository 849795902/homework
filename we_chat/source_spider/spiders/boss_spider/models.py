from source_spider.spiders.utils import DjangoItem
from django.db import models
import django.utils.timezone as timezone


class BossModel(models.Model):
    title = models.CharField(max_length=2048)
    wage = models.URLField(max_length=2048)
    md5 = models.CharField(max_length=64, unique=True)
    url = models.CharField(max_length=2048)
    company = models.CharField(max_length=2048)
    city = models.CharField(max_length=1024)
    experience = models.CharField(max_length=1024)
    education = models.CharField(max_length=1024)
    describe = models.TextField()
    create_time = models.DateTimeField(default=timezone.now)
    update_time = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "boss_source"


class BossModelMeta(DjangoItem):
    django_model = BossModel
