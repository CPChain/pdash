from django.core.cache import cache
from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST
from rest_framework.views import APIView

from cpchain.market.account.permissions import AlreadyLoginUser
from cpchain.market.account.serializers import *
from cpchain.market.market.utils import *

logger = logging.getLogger(__name__)


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

        try:
            address = get_address_from_public_key_object(public_key)
            logger.info("address:%s" % address)
            WalletUser(address=address,
                       public_key=public_key
                       ).save()
            return self.generate_verify_code(public_key, is_new=True)
        except:
            logger.exception("login error with public_key:%s" % public_key)
            return Response("login error", status=HTTP_400_BAD_REQUEST)

    def generate_verify_code(self, public_key, is_new=False):
        nonce = generate_random_str(6)
        logger.info("put cache public_key:%s, nonce:%s" % (public_key, nonce))
        cache.set(public_key, nonce, 1000)
        status = 2 if is_new else 1
        return create_invalid_response(status=status, message=nonce)


class UserLoginConfirmAPIView(APIView):
    """
    API endpoint that used to confirm login code and create token.
    """
    queryset = WalletUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

    @ExceptionHandler
    def post(self, request):
        data = request.data
        public_key_string = data.get(PUBLIC_KEY)
        signature = data.get("code")
        logger.info("public_key_string:%s,signature:%s" % (public_key_string, signature))
        if public_key_string is None or signature is None:
            logger.info("public_key is None or code is None. public_key:%s" % public_key_string)
            return create_invalid_response()

        verify_code = cache.get(public_key_string)
        if verify_code is None:
            logger.info("verify_code not found for public_key:%s" % public_key_string)
            return create_invalid_response()

        if not is_valid_signature(public_key_string, verify_code, signature):
            return create_invalid_response()

        user = WalletUser.objects.get(public_key__exact=public_key_string)

        try:
            existing_token = Token.objects.get(public_key=public_key_string)
        except Token.DoesNotExist:
            existing_token = Token.objects.create(user=user, public_key=public_key_string)

        serializer = TokenSerializer(existing_token)
        return create_login_success_data_response(serializer.data['key'])


class LogoutAPIView(APIView):
    """
    API endpoint that logout.
    """

    @ExceptionHandler
    def post(self, request):
        public_key = get_header(request)
        token = get_header(request, HTTP_MARKET_TOKEN)

        logger.info("public_key:%s,code:%s" % (public_key,token))
        if public_key is None or token is None:
            logger.info("public_key is None or token is None. public_key:%s" % public_key)
            return create_invalid_response()

        existing_token = Token.objects.get(public_key=public_key)
        serializer = TokenSerializer(existing_token)
        if serializer.data['key'] != token:
            return create_invalid_response()

        existing_token.delete()
        return create_login_success_data_response("logout success")


class UpdateProfileAPIView(APIView):
    queryset = WalletUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AlreadyLoginUser,]

    """
    API endpoint that update profile.
    """
    @ExceptionHandler
    def post(self, request):
        data = request.data
        public_key = data.get(PUBLIC_KEY)
        logger.info("public_key:%s" % public_key)

        user = WalletUser.objects.get(public_key=public_key)

        # update profile
        serializer = UserRegisterSerializer(user, data=data)

        if serializer.is_valid(raise_exception=True):
            serializer.update(user,data)
            return create_success_response()


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows Products to be viewed by anyone.
    """
    queryset = WalletUser.objects.all()
    serializer_class = UserSerializer
