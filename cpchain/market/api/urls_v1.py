from django.conf.urls import url, include
from django.contrib import admin
from rest_framework import routers
from .views import *

router = routers.DefaultRouter()
router.register(r'wallet_users', UserViewSet)
router.register(r'products', ProductViewSet)

urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^register', UserRegisterAPIView.as_view(),name='register'),
    url(r'^login', UserLoginAPIView.as_view(),name='login'),
    url(r'^confirm', UserLoginConfirmAPIView.as_view(),name='confirm'),
    url(r'^product', ProductAPIViewSet.as_view(),name='product'),
    url(r'^logout', LogoutAPIView.as_view(),name='logout'),
]
