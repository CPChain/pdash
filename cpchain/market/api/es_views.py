from cpchain.market.market.es_client import es_client
from rest_framework_elasticsearch import es_views, es_pagination, es_filters
# from .permissions import IsOwnerOrReadOnly, IsOwner
from .search_indexes import ProductIndex
from .utils import *

logger = logging.getLogger(__name__)


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
        'market_hash',
    )


# def bulk_indexing_product():
#     """
#     bulk indexing products
#     :return:
#     """
#     print("bulk indexing products")
#     ProductIndex.init()
#     bulk(client=es_client, actions=(b.indexing() for b in Product.objects.all().iterator()))


