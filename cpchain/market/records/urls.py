from django.conf.urls import url, include
from rest_framework import routers

from cpchain.market.proxy.views import ProxyViewSet

router = routers.DefaultRouter()

urlpatterns = []
