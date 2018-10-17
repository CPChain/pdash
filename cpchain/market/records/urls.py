from django.conf.urls import url, include
from rest_framework import routers

from cpchain.market.records.views import RecordViewSet

router = routers.DefaultRouter()
router.register(r'record', RecordViewSet)

urlpatterns = [
    url(r'^', include(router.urls)),
]
