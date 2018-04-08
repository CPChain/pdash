from django.db.models import Q
from django.http import JsonResponse, HttpResponse
from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from rest_framework.views import APIView

from django.core.cache import cache

from .permissions import IsOwnerOrReadOnly
from .serializers import *
from .models import Product, Token, WalletMsgSequence
from .utils import *

import logging

logger = logging.getLogger(__name__)

PUBLIC_KEY = "public_key"
VERIFY_CODE = "code"
TIMEOUT = 1000


class UserLoginAPIView(APIView):
    """
    API endpoint that used to login and fetch verify code.
    """
    queryset = WalletUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        data = request.data
        public_key = data.get(PUBLIC_KEY)

        # if is existing public key, generate verify code and put it into cache
        if WalletUser.objects.filter(public_key__exact=public_key):
            return self.generate_verify_code(public_key)

        # register wallet user, generate verify code and put it into cache
        serializer = UserRegisterSerializer(data=data)

        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return self.generate_verify_code(public_key)

        return Response(serializer.errors, status= HTTP_400_BAD_REQUEST)

    def generate_verify_code(self, public_key):
        # nonce = generate_random_str(6)
        nonce = "qZaQ6S"
        logger.info("put cache public_key:" + public_key + ", nonce:" + nonce)
        cache.set(public_key, nonce, TIMEOUT)
        return JsonResponse({"success": True, "message": nonce})


class UserLoginConfirmAPIView(APIView):
    """
    API endpoint that used to confirm login code and create token.
    """
    queryset = WalletUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        data = request.data
        public_key = data.get(PUBLIC_KEY)
        signature = data.get(VERIFY_CODE)
        logger.info("public_key:" + str(public_key) + ",signature:" + str(signature))
        if public_key is None or signature is None:
            logger.info("public_key is None or code is None. public_key:" + str(public_key))
            return create_invalid_response()

        verify_code = cache.get(public_key)
        if verify_code is None:
            logger.info("verify_code not found for public_key:" + public_key)
            return create_invalid_response()

        if not is_valid_signature(public_key, verify_code, signature):
            return create_invalid_response()

        try:
            user = WalletUser.objects.get(public_key__exact=public_key)
        except WalletUser.DoesNotExist:
            return create_invalid_response()

        try:
            existing_token = Token.objects.get(public_key=public_key)
        except Token.DoesNotExist:
            existing_token = Token.objects.create(user=user, public_key=public_key)

        serializer = TokenSerializer(existing_token)
        return JsonResponse({"success": True, "message": serializer.data['key']})


def create_invalid_response():
    return JsonResponse({"success": False, "message": "invalid request."})


class LogoutAPIView(APIView):
    """
    API endpoint that logout.
    """
    def post(self, request):
        data = request.data
        public_key = data.get(PUBLIC_KEY)
        token = data.get('token')
        logger.info("public_key:" + str(public_key) + ",code:" + str(token))
        if public_key is None or token is None:
            logger.info("public_key is None or token is None. public_key:" + str(public_key))
            return create_invalid_response()

        try:
            existing_token = Token.objects.get(public_key=public_key)
            serializer = TokenSerializer(existing_token)
            if serializer.data['key'] != token:
                return create_invalid_response()

            existing_token.delete()
            return JsonResponse({"success": True, "message": "logout success"})
        except Token.DoesNotExist:
            logger.info("logout public_key:" + str(public_key) + " not login")
            return create_invalid_response()


def create_success_response():
    return JsonResponse({'status': 1, 'message': 'success'})


class ProductPublishAPIViewSet(APIView):
    """
    API endpoint that allows query products.
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    # permission_classes = (AllowAny,)
    permission_classes = (IsOwnerOrReadOnly,)

    def post(self, request):
        public_key = self.request.META.get('HTTP_MARKET_KEY')
        logger.info("public_key:" + str(public_key))

        if public_key is None:
            return create_invalid_response()

        data = request.data
        try:
            msg_seq = WalletMsgSequence.objects.get(public_key=public_key)
            msg_seq.seq = msg_seq.seq+1
        except WalletMsgSequence.DoesNotExist:
            msg_seq = WalletMsgSequence(seq=0,public_key=public_key,user=WalletUser.objects.get(public_key=public_key))
            print("msg_seq:" + str(msg_seq.seq))

        print("seq:" + str(msg_seq.seq))
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
        # print("owner_address:"+product.owner_address)
        # print("product.signature:"+product.signature)
        # print("signature_source:"+signature_source)
        is_valid_signature = verify_signature(product.owner_address, product.signature, signature_source)
        print("is_valid_signature:" + str(is_valid_signature) + ",signature_source:" + str(signature_source))

        if not is_valid_signature:
            logger.error("invalid_signature")
            return create_invalid_response()

        # generate msg hash
        msg_hash_source = product.get_msg_hash()
        print("msg_hash_source:" + msg_hash_source)
        product.msg_hash = generate_msg_hash(msg_hash_source)
        print("msg_hash:" + product.msg_hash)
        data['msg_hash'] = product.msg_hash
        data['seq']=msg_seq.seq

        serializer = ProductSerializer(data=data)

        try:
            if serializer.is_valid(raise_exception=True):
                msg_seq.save()
                serializer.save(owner=WalletUser.objects.get(public_key=public_key))
                return create_success_response()
        except Exception:
            exstr = traceback.format_exc()
            print(exstr)
            pass

        return create_invalid_response()

    def get(self, request):
        logger.info('this is product get')
        params = request.query_params
        keyword = params.get('keyword')
        if keyword is not None:
            logger.info("keyword is ", keyword)
            queryset = Product.objects.filter(
                Q(title__contains=keyword) | Q(description__contains=keyword) | Q(tags__contains=keyword))
        else:
            queryset = Product.objects.all()

        serializer = ProductSerializer(queryset, many=True)
        return Response(data=serializer.data)


class ProductStatusChangeAPIViewSet(APIView):
    """
    update product status
    """
    queryset = Product.objects.all()
    serializer_class = ProductUpdateSerializer
    # permission_classes = (AllowAny,)
    permission_classes = (IsOwnerOrReadOnly,)

    def post(self, request):
        public_key = self.request.META.get('HTTP_MARKET_KEY')
        logger.info("public_key:" + str(public_key))

        if public_key is None:
            return create_invalid_response()

        try:
            product = Product.objects.get(owner_address=public_key,msg_hash=request.data['msg_hash'])
        except Product.DoesNotExist:
            return HttpResponse(status=404)

        data = request.data
        data['owner_address'] = public_key
        serializer = ProductUpdateSerializer(product,data=data)
        if serializer.is_valid(raise_exception=True):
            logger.info("update product status")
            serializer.update(product,data)
            return create_success_response()

        return create_invalid_response()


class ProductViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows query products.
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    # permission_classes = (AllowAny,)
    permission_classes = (IsOwnerOrReadOnly,)

    def perform_create(self, serializer):
        public_key = self.request.META.get('HTTP_MARKET_KEY')
        logger.info("create product for public_key:" + str(public_key))

        if public_key is None:
            logger.info('refuse to save product')
            return create_invalid_response()

        serializer.save(owner=WalletUser.objects.get(public_key=public_key))

    def list(self, request, *args, **kwargs):
        """
        query product by keyword
        """
        params = request.query_params
        keyword = params.get('keyword')
        if keyword is not None:
            logger.info("keyword is ", keyword)
            queryset = Product.objects.filter(Q(title__contains=keyword) | Q(description__contains=keyword))
        else:
            queryset = Product.objects.all()

        serializer = ProductSerializer(queryset, many=True)
        return Response(data=serializer.data)


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows Products to be viewed by anyone.
    """
    queryset = WalletUser.objects.all()
    serializer_class = UserSerializer
