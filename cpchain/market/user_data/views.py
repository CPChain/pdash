from django.db.models import Q
from django.http import JsonResponse
from rest_framework.response import Response
from rest_framework.views import APIView

from cpchain.market.account.permissions import IsOwner
from cpchain.market.account.utils import *
from cpchain.market.product.models import WalletMsgSequence
from cpchain.market.product.serializers import *
from cpchain.market.user_data.models import UploadFileInfo, BuyerFileInfo, UserInfoVersion
from cpchain.market.user_data.serializers import UploadFileInfoSerializer, UserInfoVersionSerializer, \
    BuyerFileInfoSerializer

logger = logging.getLogger(__name__)

PUBLIC_KEY = "public_key"
VERIFY_CODE = "code"
TIMEOUT = 1000


def create_invalid_response():
    return JsonResponse({"success": False, "message": "invalid request."})


def create_success_response():
    return JsonResponse({'status': 1, 'message': 'success'})


class UploadFileInfoAPIViewSet(APIView):
    """
    TODO API endpoint that allows save UploadFileInfo.
    """
    queryset = UploadFileInfo.objects.all()
    serializer_class = UploadFileInfoSerializer
    permission_classes = (IsOwner,)

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


class PullUserInfoAPIViewSet(APIView):
    """
    TODO API endpoint that allows pull user info (UploadFileInfo,BuyerFileInfo) by owner.
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = (IsOwner,)

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


class BuyerFileInfoAPIViewSet(APIView):
    """
    TODO API endpoint that allows save BuyerFileInfo.
    """
    queryset = BuyerFileInfo.objects.all()
    serializer_class = BuyerFileInfoSerializer
    permission_classes = (IsOwner,)

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


class UserInfoVersionAPIViewSet(APIView):
    """
    TODO API endpoint that allows query latest user data version by owner.
    """
    queryset = UserInfoVersion.objects.all()
    serializer_class = UserInfoVersionSerializer
    permission_classes = (IsOwner,)

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
