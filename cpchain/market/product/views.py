from django.db.models import Q
from django.http import JsonResponse
from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from cpchain.market.comment.models import SummaryComment
from cpchain.market.product.models import WalletMsgSequence, MyTag, MySeller
from cpchain.market.product.serializers import *
from cpchain.market.account.permissions import IsOwnerOrReadOnly, AlreadyLoginUser
from cpchain.market.market.utils import *

logger = logging.getLogger(__name__)

PUBLIC_KEY = "public_key"
VERIFY_CODE = "code"
TIMEOUT = 1000


def create_invalid_response():
    return JsonResponse({"success": False, "message": "invalid request."})


def create_success_response():
    return JsonResponse({'status': 1, 'message': 'success'})


class ProductPublishAPIViewSet(APIView):
    """
    API endpoint that allows publish products.
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = (IsOwnerOrReadOnly,)

    def post(self, request):
        public_key = self.request.META.get('HTTP_MARKET_KEY')
        logger.info("public_key:%s" % public_key)

        if public_key is None:
            return create_invalid_response()

        data = request.data
        try:
            msg_seq = WalletMsgSequence.objects.get(public_key=public_key)
            msg_seq.seq = msg_seq.seq + 1
        except WalletMsgSequence.DoesNotExist:
            msg_seq = WalletMsgSequence(seq=0, public_key=public_key,
                                        user=WalletUser.objects.get(public_key=public_key))
            logger.debug("msg_seq:%s" % msg_seq.seq)

        logger.debug("seq:%s" % msg_seq.seq)
        now = timezone.now()
        product = Product(data)
        product.seq = msg_seq.seq
        product.owner_address = data['owner_address']
        product.title = data['title']
        product.description = data['description'],
        product.price = data['price'],
        product.created = now,
        product.start_date = data['start_date']
        product.end_date = data['end_date']
        product.signature = data['signature']
        product.file_md5 = data['file_md5']
        product.owner_address = data['owner_address']

        signature_source = product.get_signature_source()
        logger.debug("owner_address:%s" % product.owner_address)
        logger.debug("product.signature:%s" % product.signature)
        logger.debug("signature_source:%s" % signature_source)
        is_valid_sign = verify_signature(product.owner_address, product.signature, signature_source)
        logger.debug("product.signature:%s" % str(product.signature))
        logger.debug("is_valid_signature:%s,signature_source:%s" % (is_valid_sign, signature_source))

        if not is_valid_sign:
            logger.error("invalid_signature")
            return create_invalid_response()

        # generate msg hash
        msg_hash_source = product.get_msg_hash_source()
        logger.debug("msg_hash_source:%s" % msg_hash_source)
        product.msg_hash = generate_msg_hash(msg_hash_source)
        logger.debug("msg_hash:%s" % product.msg_hash)
        data['msg_hash'] = product.msg_hash
        data['seq'] = msg_seq.seq

        serializer = ProductSerializer(data=data)

        try:
            if serializer.is_valid(raise_exception=True):
                msg_seq.save()
                serializer.save(owner=WalletUser.objects.get(public_key=public_key))
                return JsonResponse({'status': 1, 'message': 'success', 'data': {'market_hash': product.msg_hash}})
        except Exception:
            logger.exception("save product error")

        return create_invalid_response()


class MyProductSearchAPIViewSet(APIView):
    """
    API endpoint that allows query products by owner.
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = (AlreadyLoginUser,)

    def get(self, request):
        public_key = self.request.META.get('HTTP_MARKET_KEY')
        logger.info("public_key:%s" % public_key)
        params = request.query_params
        keyword = params.get('keyword')
        if keyword is not None and len(keyword)!=0:
            logger.debug("keyword is %s" % keyword)
            queryset = Product.objects.filter(owner_address=public_key).filter(
                Q(title__contains=keyword) | Q(description__contains=keyword) | Q(tags__contains=keyword))
        else:
            queryset = Product.objects.filter(owner_address=public_key)

        serializer = ProductSerializer(queryset, many=True)
        return Response(data=serializer.data)


class MyProductPagedSearchAPIViewSet(APIView):
    """
    API endpoint that allows query products by owner.
    sample url:
    http://localhost:8000/api/v1/my_product_paged/search/?page=1&keyword=777
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = (AlreadyLoginUser,)

    def get(self, request):

        public_key = self.request.META.get('HTTP_MARKET_KEY')
        logger.info("public_key:%s" % public_key)
        params = request.query_params
        keyword = params.get('keyword')
        if keyword is not None and len(keyword)!=0:
            logger.debug("keyword is %s" % keyword)
            queryset = Product.objects.filter(owner_address=public_key).filter(
                Q(title__contains=keyword) | Q(description__contains=keyword) | Q(tags__contains=keyword))
        else:
            queryset = Product.objects.filter(owner_address=public_key)

        pg = PageNumberPagination()
        page_set = pg.paginate_queryset(queryset=queryset, request=request, view=self)
        serializer = ProductSerializer(page_set, many=True)
        return pg.get_paginated_response(serializer.data)


class ProductSearchAPIViewSet(APIView):
    """
    API endpoint that allows query products.
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = (AllowAny,)

    def get(self, request):
        params = request.query_params
        keyword = params.get('keyword')
        if keyword is not None:
            logger.debug("keyword is %s" % keyword)
            queryset = Product.objects.filter(status=0).filter(
                Q(title__contains=keyword) | Q(description__contains=keyword) |
                Q(tags__contains=keyword) | Q(msg_hash=keyword)
            )
        else:
            queryset = Product.objects.filter(status=0)

        serializer = ProductSerializer(queryset, many=True)
        return Response(data=serializer.data)


class ProductPagedSearchAPIViewSet(APIView):
    """
    API endpoint that allows query products.
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = (AllowAny,)

    def get(self, request):
        params = request.query_params
        keyword = params.get('keyword')
        if keyword is not None:
            logger.debug("keyword is %s" % keyword)
            queryset = Product.objects.filter(status=0).filter(
                Q(title__contains=keyword) | Q(description__contains=keyword) | Q(tags__contains=keyword))
        else:
            queryset = Product.objects.filter(status=0)

        pg = PageNumberPagination()
        page_set = pg.paginate_queryset(queryset=queryset, request=request, view=self)
        serializer = ProductSerializer(page_set, many=True)
        return pg.get_paginated_response(serializer.data)


class BaseProductStatusAPIViewSet(APIView):
    """
    update product status to normal
    """
    queryset = Product.objects.all()
    serializer_class = ProductUpdateSerializer
    permission_classes = (IsOwnerOrReadOnly,)

    def post(self, request):
        raise BaseException("not implemented")

    def update_product_status(self, request, status):
        public_key = self.request.META.get('HTTP_MARKET_KEY')
        logger.debug("public_key:%s status:%s" % (public_key, status))
        if public_key is None:
            return create_invalid_response()
        try:
            product = Product.objects.get(owner_address=public_key, msg_hash=request.data['msg_hash'])
        except Product.DoesNotExist:
            return create_invalid_response()
        data = request.data
        data['status'] = status
        serializer = ProductUpdateSerializer(product, data=data)
        if not serializer.is_valid(raise_exception=True):
            return create_invalid_response()
        logger.debug("update product status")
        serializer.update(product, data)
        response = create_success_response()
        return response


class ProductShowAPIViewSet(BaseProductStatusAPIViewSet):
    """
    update product status to normal
    """
    queryset = Product.objects.all()
    serializer_class = ProductUpdateSerializer
    permission_classes = (IsOwnerOrReadOnly,)

    def post(self, request):
        return self.update_product_status(request, "0")


class ProductHideAPIViewSet(BaseProductStatusAPIViewSet):
    """
    update product status to hide
    """
    queryset = Product.objects.all()
    serializer_class = ProductUpdateSerializer
    permission_classes = (IsOwnerOrReadOnly,)

    def post(self, request):
        return self.update_product_status(request, "1")


class ProductViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows query products.
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = (IsOwnerOrReadOnly,)

    def perform_create(self, serializer):
        public_key = self.request.META.get('HTTP_MARKET_KEY')
        logger.debug("create product for public_key:%s" % public_key)

        if public_key is None:
            logger.debug('public_key is none,refuse to save product')
            return create_invalid_response()

        serializer.save(owner=WalletUser.objects.get(public_key=public_key))

    def list(self, request, *args, **kwargs):
        """
        query product by keyword
        """
        params = request.query_params
        keyword = params.get('keyword')
        if keyword is not None:
            logger.debug("keyword is %s" % keyword)
            queryset = Product.objects.filter(Q(title__contains=keyword) | Q(description__contains=keyword))
        else:
            queryset = Product.objects.all()

        serializer = ProductSerializer(queryset, many=True)
        return Response(data=serializer.data)


class RecommendProductsAPIView(APIView):
    """
    API endpoint that allows query recommend products.
    """
    queryset = Product.objects.all()
    serializer_class = RecommendProductSerializer
    permission_classes = (AllowAny,)

    def get(self, request):
        # FIXME query current user following tags,query top 10 products with tags
        queryset = Product.objects.filter(status=0)[0:10]
        serializer = RecommendProductSerializer(queryset, many=True)
        products = serializer.data

        # fill username and rating for each product,return to client
        product_list = []
        for p in products:
            pk = p['owner_address']
            u = WalletUser.objects.get(public_key=pk)

            p['username'] = '' if not u else u.username
            # query average rating from SummaryComment table
            comment,_ = SummaryComment.objects.get_or_create(market_hash=p['msg_hash'])
            p['avg_rating'] = 1 if not comment else comment.avg_rating
            product_list.append(p)

        return JsonResponse({'status': 1, 'message': 'success', 'data': product_list})


class ProductSalesQuantityAddAPIView(APIView):
    """
    API endpoint that allows add product sales quantity.
    """
    queryset = Product.objects.all()
    serializer_class = ProductSalesQuantitySerializer
    permission_classes = (AlreadyLoginUser,)

    def post(self, request):
        return self.increase_product_sales_quantity(request)

    def increase_product_sales_quantity(self, request):
        public_key = self.request.META.get('HTTP_MARKET_KEY')
        market_hash = request.data['market_hash']
        logger.debug("public_key:%s market_hash:%s" % (public_key, market_hash))

        obj, created = SalesQuantity.objects.get_or_create(market_hash=request.data['market_hash'])
        if not created :
            serializer = ProductSalesQuantitySerializer(obj, data=request.data)
            if not serializer.is_valid(raise_exception=True):
                return create_invalid_response()

            logger.debug("update product number")
            obj = serializer.update(obj, request.data)

        logger.debug("obj.quantity:%s" % obj.quantity)
        return JsonResponse({'status': 1, 'message': 'success', 'data': obj.quantity})


class ProductTagSubscribeAPIView(APIView):
    """
    API endpoint that allows add ProductTagSubscribe
    """
    queryset = MyTag.objects.all()
    permission_classes = (AlreadyLoginUser,)

    def post(self, request):
        public_key = self.request.META.get('HTTP_MARKET_KEY')
        tag = request.data['tag']
        logger.debug("public_key:%s tag:%s" % (public_key, tag))

        obj, _ = MyTag.objects.get_or_create(public_key=public_key, tag=request.data['tag'])
        return JsonResponse({'status': 1, 'message': 'success'})


class ProductTagUnsubscribeAPIView(APIView):
    """
    API endpoint that allows add ProductTagUnsubscribe
    """
    queryset = MyTag.objects.all()
    permission_classes = (AlreadyLoginUser,)

    def post(self, request):
        public_key = self.request.META.get('HTTP_MARKET_KEY')
        tag = request.data['tag']
        logger.debug("delete tag:%s for public_key:%s" % (tag, public_key))
        MyTag.objects.filter(public_key=public_key, tag=request.data['tag']).delete()
        return JsonResponse({'status': 1, 'message': 'success'})


class MyTaggedProductSearchAPIView(APIView):
    """
    API endpoint that allows query products.
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = (AlreadyLoginUser,)

    def get(self, request):
        # TODO ================================================
        public_key = self.request.META.get('HTTP_MARKET_KEY')
        tag_list = MyTag.objects.filter(public_key=public_key)
        logger.debug('taglist:%s' % tag_list)
        keyword = ','.join(x.tag for x in tag_list)

        logger.debug("keyword is %s" % keyword)

        queryset = Product.objects.filter(status=0).filter(Q(tags__contains=keyword))

        page_set = PageNumberPagination().paginate_queryset(queryset=queryset, request=request, view=self)
        serializer = ProductSerializer(page_set, many=True)

        return JsonResponse({'status': 1, 'message': 'success', "data": serializer.data})


class ProductSellerSubscribeAPIView(APIView):
    """
    API endpoint that allows subscribe ProductSeller
    """
    queryset = MySeller.objects.all()
    permission_classes = (AlreadyLoginUser,)

    def post(self, request):
        public_key = self.request.META.get('HTTP_MARKET_KEY')
        seller_public_key = request.data['seller_public_key']
        logger.debug("public_key:%s seller_public_key:%s" % (public_key, seller_public_key))

        obj, _ = MySeller.objects.get_or_create(public_key=public_key,
                                                seller_public_key=request.data['seller_public_key'])
        return JsonResponse({'status': 1, 'message': 'success'})


class ProductSellerUnsubscribeAPIView(APIView):
    """
    API endpoint that allows unsubscribe ProductSeller
    """
    queryset = MySeller.objects.all()
    permission_classes = (AlreadyLoginUser,)

    def post(self, request):
        public_key = self.request.META.get('HTTP_MARKET_KEY')
        seller_public_key = request.data['seller_public_key']
        logger.debug("delete seller_public_key:%s for public_key:%s" % (seller_public_key, public_key))
        MySeller.objects.filter(public_key=public_key, seller_public_key=request.data['seller_public_key']).delete()
        return JsonResponse({'status': 1, 'message': 'success'})


class MyTaggedSellerSearchAPIView(APIView):
    """
    API endpoint that allows query products.
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = (AlreadyLoginUser,)

    def get(self, request):
        # TODO ================================================
        public_key = self.request.META.get('HTTP_MARKET_KEY')
        seller_list = MySeller.objects.filter(public_key=public_key)
        keyword = ','.join(x.seller_public_key for x in seller_list)
        logger.debug('keyword:%s' % keyword)

        queryset = Product.objects.filter(status=0).filter(Q(owner_address=keyword))
        page_set = PageNumberPagination().paginate_queryset(queryset=queryset, request=request, view=self)
        serializer = ProductSerializer(page_set, many=True)
        return JsonResponse({'status': 1, 'message': 'success', "data": serializer.data})
