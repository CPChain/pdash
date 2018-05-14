from django.conf.urls import url, include
from rest_framework import routers

from cpchain.market.comment.views import ProductCommentListAPIView, ProductSummaryCommentSearchAPIView, \
    ProductCommentAddAPIView
from cpchain.market.product.es_views import ESProductView
from cpchain.market.product.views import *

router = routers.DefaultRouter()
router.register(r'products', ProductViewSet)

urlpatterns = [
    url(r'^comment/list/$', ProductCommentListAPIView.as_view(), name='comment_list'),
    url(r'^comment/add/$', ProductCommentAddAPIView.as_view(), name='comment_add'),
    url(r'^summary_comment/$', ProductSummaryCommentSearchAPIView.as_view(), name='get_summary_comment'),
]