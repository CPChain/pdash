from django.conf.urls import url

from cpchain.market.main.views import *

urlpatterns = (
    url(r'^carousel/list/$', CarouselQueryAPIView.as_view(), name='carousel_list'),
    url(r'^carousel/add/$', CarouselAddAPIView.as_view(), name='carousel_add'),
    url(r'^hot_tag/list/$', HotTagQueryAPIView.as_view(), name='hot_tag_list'),
    url(r'^hot_tag/add/$', HotTagAddAPIView.as_view(), name='hot_tag_add'),
    url(r'^promotion/list/$', PromotionQueryAPIView.as_view(), name='promotion_list'),
    url(r'^promotion/add/$', PromotionAddAPIView.as_view(), name='promotion_add'),

)
