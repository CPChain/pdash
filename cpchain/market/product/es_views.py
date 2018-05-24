from rest_framework.response import Response

from cpchain.market.market.es_client import es_client
from cpchain.market.product.models import Product
from rest_framework_elasticsearch import es_views, es_pagination, es_filters
from .search_indexes import ProductIndex


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
        "created",
    )
    es_filter_fields = (
        es_filters.ESFieldFilter('tag', 'tags'),
        es_filters.ESFieldFilter('status', 'status'),
        es_filters.ESFieldFilter('seller', 'owner_address'),
        es_filters.ESFieldFilter('pid', 'market_hash')
    )
    es_search_fields = (
        'title',
        'description',
        'tags',
    )

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def list(self, request, *args, **kwargs):
        search = self.do_search()

        page = self.paginate_search(search)
        page = self.fill_attrs(page)
        if page is not None:
            return self.get_paginated_response(self.es_representation(page))

        return Response(self.es_representation(search.scan()))

    def fill_attrs(self, iterable):
        return [Product.fill_attr(item) for item in iterable]
