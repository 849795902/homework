from django.conf.urls import url
from source_spider.django_api.views import *

urlpatterns = [
    url(r'^js_render/', js_render, name="js_render"),
    url(r'^get_proxy/', get_proxy, name="get_proxy")
]
