from rest_framework.response import Response

from cpchain.market.account.models import WalletUser
from cpchain.market.comment.models import SummaryComment
from cpchain.market.market.es_client import es_client
from cpchain.market.transaction.models import ProductSaleStatus
from rest_framework_elasticsearch import es_views, es_pagination, es_filters
# from .permissions import IsOwnerOrReadOnly, IsOwner
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
        # fill username, rating, sales_number
        page = self.fill_attrs(page)
        if page is not None:
            return self.get_paginated_response(self.es_representation(page))

        return Response(self.es_representation(search.scan()))

    def fill_attrs(self, iterable):
        """List of object instances."""
        return [self.fill_attr(item) for item in iterable]

    def fill_attr(self, item):
        pk = item.owner_address
        u = WalletUser.objects.get(public_key=pk)

        comment, _ = SummaryComment.objects.get_or_create(market_hash=item.market_hash)
        sale_status, _ = ProductSaleStatus.objects.get_or_create(market_hash=item.market_hash)

        item.username = '' if not u else u.username
        item.avg_rating = 1 if not comment else comment.avg_rating
        item.sales_number = 0 if not sale_status else sale_status.sales_number
        return item
