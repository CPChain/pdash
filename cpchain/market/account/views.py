from django.core.cache import cache
from django.http import JsonResponse
from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST
from rest_framework.views import APIView

from cpchain.market.account.serializers import *
from cpchain.market.account.utils import *

logger = logging.getLogger(__name__)

PUBLIC_KEY = "public_key"
VERIFY_CODE = "code"
TIMEOUT = 1000


def create_invalid_response():
    return JsonResponse({"status": 0, "message": "invalid request."})


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
            return self.generate_verify_code(public_key,is_new=True)

        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)

    def generate_verify_code(self, public_key, is_new=False):
        nonce = generate_random_str(6)
        logger.info("put cache public_key:%s, nonce:%s" % (public_key, nonce))
        cache.set(public_key, nonce, TIMEOUT)
        status = 2 if is_new else 1
        return JsonResponse({"status": status, "message": nonce})


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
        logger.info("public_key:%s,signature:%s" % (public_key, signature))
        if public_key is None or signature is None:
            logger.info("public_key is None or code is None. public_key:%s" % public_key)
            return create_invalid_response()

        verify_code = cache.get(public_key)
        if verify_code is None:
            logger.info("verify_code not found for public_key:%s" % public_key)
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
        return JsonResponse({"status": 1, "message": serializer.data['key']})


class LogoutAPIView(APIView):
    """
    API endpoint that logout.
    """

    def post(self, request):
        data = request.data
        public_key = data.get(PUBLIC_KEY)
        token = data.get('token')
        logger.info("public_key:%s,code:%s" % (public_key,token))
        if public_key is None or token is None:
            logger.info("public_key is None or token is None. public_key:%s" % public_key)
            return create_invalid_response()

        try:
            existing_token = Token.objects.get(public_key=public_key)
            serializer = TokenSerializer(existing_token)
            if serializer.data['key'] != token:
                return create_invalid_response()

            existing_token.delete()
            return JsonResponse({"status": 1, "message": "logout success"})
        except Token.DoesNotExist:
            logger.info("logout public_key:%s not login" % public_key)
            return create_invalid_response()


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows Products to be viewed by anyone.
    """
    queryset = WalletUser.objects.all()
    serializer_class = UserSerializer

