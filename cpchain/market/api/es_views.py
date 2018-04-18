# from django.db.models import Q
# from django.http import JsonResponse
# from rest_framework import viewsets
# from rest_framework.pagination import PageNumberPagination
# from rest_framework.permissions import AllowAny
# from rest_framework.response import Response
# from rest_framework.views import APIView
# from elasticsearch.helpers import bulk

from cpchain.market.market.es_client import es_client
from rest_framework_elasticsearch import es_views, es_pagination, es_filters
# from .permissions import IsOwnerOrReadOnly, IsOwner
from .search_indexes import ProductIndex
from .utils import *
# from .models import Product

# error happens here
# from cpchain.market.api.models import Product, Token, WalletMsgSequence

logger = logging.getLogger(__name__)

PUBLIC_KEY = "public_key"
VERIFY_CODE = "code"
TIMEOUT = 1000


class ESProductView(es_views.ListElasticAPIView):
    es_client = es_client
    es_model = ProductIndex
    es_pagination_class = es_pagination.ElasticLimitOffsetPagination

    es_filter_backends = (
        es_filters.ElasticFieldsFilter,
        es_filters.ElasticSearchFilter,
        es_filters.ElasticOrderingFilter,
    )
    es_ordering_fields = (
        "created_at",
        ("title.raw", "title")
    )
    es_filter_fields = (
        es_filters.ESFieldFilter('tags', 'tags'),
        es_filters.ESFieldFilter('status', 'status')
    )
    es_search_fields = (
        'tags',
        'title',
        'description',
    )


# def bulk_indexing_product():
#     """
#     bulk indexing products
#     :return:
#     """
#     print("bulk indexing products")
#     ProductIndex.init()
#     bulk(client=es_client, actions=(b.indexing() for b in Product.objects.all().iterator()))
