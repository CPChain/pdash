from django.conf.urls import url, include
from django.contrib import admin
from rest_framework import routers

from cpchain.market.api.es_views import ESProductView
from .views import *


urlpatterns = [
    # url(r'^', include(router.urls)),
]


