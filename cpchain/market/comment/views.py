from django.db.models import Q
from django.http import JsonResponse
from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from cpchain.market.comment.models import SummaryComment, Comment
from cpchain.market.comment.serializers import SummaryCommentSerializer, CommentSerializer
from cpchain.market.product.models import WalletMsgSequence, MyTag, MySeller
from cpchain.market.product.serializers import *
from cpchain.market.account.permissions import IsOwnerOrReadOnly, AlreadyLoginUser
from cpchain.market.market.utils import *

logger = logging.getLogger(__name__)


class ProductCommentListAPIView(APIView):
    """
    API endpoint that allows query Comment.
    """
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = (AllowAny,)

    def get(self, request):
        market_hash = self.request.GET.get('market_hash')
        logger.debug("market_hash is %s" % market_hash)
        queryset = Comment.objects.filter(Q(market_hash=market_hash))
        page_set = PageNumberPagination().paginate_queryset(queryset=queryset, request=request, view=self)
        serializer = CommentSerializer(page_set, many=True)

        return JsonResponse({'status': 1, 'message': 'success', "data": serializer.data})


class ProductSummaryCommentSearchAPIView(APIView):
    """
    API endpoint that allows query product summary comment.
    """
    queryset = SummaryComment.objects.all()
    serializer_class = SummaryCommentSerializer
    permission_classes = (AllowAny,)

    def get(self, request):
        market_hash = self.request.GET.get('market_hash')
        summary_comment, _ = SummaryComment.objects.get_or_create(market_hash=market_hash)
        logger.debug('summary_comment:%s' % summary_comment)
        serializer = SummaryCommentSerializer(summary_comment)
        return JsonResponse({'status': 1, 'message': 'success', "data": serializer.data})