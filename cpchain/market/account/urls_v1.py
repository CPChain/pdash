from django.conf.urls import url, include
from rest_framework import routers

from cpchain.market.account.views import *

router = routers.DefaultRouter()
router.register(r'wallet_users', UserViewSet)

urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^login', UserLoginAPIView.as_view(), name='login'),
    url(r'^confirm', UserLoginConfirmAPIView.as_view(), name='confirm'),
    url(r'^logout', LogoutAPIView.as_view(), name='logout'),
    url(r'^profile/update', UpdateProfileAPIView.as_view(), name='update_profile'),
]


