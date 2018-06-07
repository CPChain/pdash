from django.utils.http import unquote
from django.db.models import Q
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView

from cpchain.market.account.models import WalletUser
from cpchain.market.account.permissions import AlreadyLoginUser
from cpchain.market.comment.models import SummaryComment, Comment
from cpchain.market.comment.serializers import SummaryCommentSerializer, CommentSerializer
from cpchain.market.market.utils import *
from cpchain.market.transaction.models import TransactionDetail

logger = logging.getLogger(__name__)


class ProductCommentListAPIView(APIView):
    """
    API endpoint that allows query Comment.
    """
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = (AllowAny,)

    @ExceptionHandler
    def get(self, request):
        market_hash = unquote(self.request.GET.get('market_hash'))
        logger.debug("market_hash is %s" % market_hash)
        queryset = Comment.objects.filter(Q(market_hash=market_hash)).order_by('-created')
        page_set = PageNumberPagination().paginate_queryset(
            queryset=queryset,
            request=request,
            view=self
        )
        serializer = CommentSerializer(page_set, many=True)
        comments = serializer.data
        comment_list = []
        for item in comments:
            comment_list.append(Comment.fill_attr(item))

        return create_success_data_response(comment_list)


class ProductCommentAddAPIView(APIView):
    """
    API endpoint that allows add Comment.
    """
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = (AlreadyLoginUser,)

    @ExceptionHandler
    def post(self, request):
        data = request.data
        logger.info("data:%s" % data)
        public_key = get_header(request)
        market_hash = unquote(data['market_hash'])
        logger.info("public_key:%s,market_hash:%s", public_key, market_hash)

        user = WalletUser.objects.get(public_key=public_key)
        logger.info("user:%s" % user)
        buyer_address = user.address
        logger.info("buyer_address:%s" % buyer_address)
        # check if current user(public_key) buy the product(market_hash)
        exists_transaction = TransactionDetail.objects.filter(
            buyer_address=buyer_address).filter(
            market_hash=market_hash).exists()
        if not exists_transaction:
            logger.info('no tx,invalid comment request from %s' % public_key)
            return create_invalid_response()

        serializer = CommentSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return create_success_response()


class ProductSummaryCommentSearchAPIView(APIView):
    """
    API endpoint that allows query product summary comment.
    """
    queryset = SummaryComment.objects.all()
    serializer_class = SummaryCommentSerializer
    permission_classes = (AllowAny,)

    @ExceptionHandler
    def get(self, request):

        market_hash = unquote(self.request.GET.get('market_hash'))
        summary_comment, _ = SummaryComment.objects.get_or_create(market_hash=market_hash)
        logger.debug('summary_comment:%s' % summary_comment)
        serializer = SummaryCommentSerializer(summary_comment)
        return create_success_data_response(serializer.data)