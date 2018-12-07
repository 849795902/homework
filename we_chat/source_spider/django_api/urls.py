from django.conf.urls import url
from source_spider.django_api.views import *

urlpatterns = [
    url(r'^js_render/', js_render, name="js_render")
]
