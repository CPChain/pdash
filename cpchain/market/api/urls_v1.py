from django.conf.urls import url, include
from django.contrib import admin
from rest_framework import routers
from .views import *

router = routers.DefaultRouter()
router.register(r'wallet_users', UserViewSet)
router.register(r'products', ProductViewSet)

urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^login', UserLoginAPIView.as_view(),name='login'),
    url(r'^confirm', UserLoginConfirmAPIView.as_view(),name='confirm'),
    url(r'^my_product/search/$', MyProductSearchAPIViewSet.as_view(), name='my_product_search'),
    url(r'^my_product_paged/search/$', MyProductPagedSearchAPIViewSet.as_view(), name='my_product_paged_search'),
    url(r'^product/show/$', ProductShowAPIViewSet.as_view(), name='product_show'),
    url(r'^product/hide/$', ProductHideAPIViewSet.as_view(), name='product_hide'),
    url(r'^product/publish/$', ProductPublishAPIViewSet.as_view(), name='product_publish'),
    url(r'^product/search/$', ProductSearchAPIViewSet.as_view(), name='product_search'),
    url(r'^product_paged/search/$', ProductPagedSearchAPIViewSet.as_view(), name='product_paged_search'),
    url(r'^logout', LogoutAPIView.as_view(), name='logout'),
]
