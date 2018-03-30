# accept public key from client(wallet),
# response string with encrypted(random string)
# if client decrypt correctly ,login success
# else response with HTTP_400_BAD_REQUEST
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
from .models import Product,Token
from .utils import *

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
            return self.generate_verifycode(public_key)

        # register wallet user, generate verify code and put it into cache
        serializer = UserRegisterSerializer(data=data)

        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return self.generate_verifycode(public_key)

        return Response(serializer.errors, status= HTTP_400_BAD_REQUEST)

    def generate_verifycode(self, public_key):
        code = generate_random_str(6)
        print("put cache public_key:" + public_key + ", code:" + code)
        cache.set(public_key, code, TIMEOUT)
        # response with encrypted verify code
        encrypted_code = encrypte_verify_code(public_key, code)
        return JsonResponse({"success": True, "message": encrypted_code})


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
        code = data.get(VERIFY_CODE)
        print("public_key:" + str(public_key) + ",code:" + str(code))
        if public_key is None or code is None:
            print("public_key is None or code is None. public_key:" + str(public_key))
            return create_invalid_response()

        verify_code = cache.get(public_key)
        print("verify_code:" + str(verify_code))
        if verify_code is None:
            print("verify_code not found for public_key:" + public_key)
            return create_invalid_response()

        if not is_valid_verify_code(public_key, verify_code):
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


class UserRegisterAPIView(APIView):
    """
    API endpoint that used to register user account.
    """
    queryset = WalletUser.objects.all()
    serializer_class = UserRegisterSerializer
    permission_classes = (AllowAny,)

    def post(self, request):
        data = request.data
        public_key = data.get(PUBLIC_KEY)
        if WalletUser.objects.filter(public_key__exact=public_key):
            return Response("public_key already exists!", HTTP_400_BAD_REQUEST)
        serializer = UserRegisterSerializer(data=data)

        if serializer.is_valid(raise_exception=True):
            serializer.save()
            d = {
                'status': 1,
                'message': 'success',
            }
            return JsonResponse(d)
        return Response(serializer.errors, status= HTTP_400_BAD_REQUEST)


class LogoutAPIView(APIView):
    """
    API endpoint that logout.
    """
    def post(self, request):
        data = request.data
        public_key = data.get(PUBLIC_KEY)
        token = data.get('token')
        print("public_key:" + str(public_key) + ",code:" + str(token))
        if public_key is None or token is None:
            print("public_key is None or token is None. public_key:" + str(public_key))
            return create_invalid_response()

        try:
            existing_token = Token.objects.get(public_key=public_key)
            serializer = TokenSerializer(existing_token)
            if serializer.data['key'] != token:
                return create_invalid_response()

            existing_token.delete()
            return JsonResponse({"success": True, "message": "logout success"})
        except Token.DoesNotExist:
            print("logout public_key:" + str(public_key) + " not login")
            return create_invalid_response()


class ProductViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows query products.
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = (AllowAny,)
    # permission_classes = (IsOwnerOrReadOnly,)

    def perform_create(self, serializer):
        user_id = self.request.session.get('user_id')
        print(user_id)

        # TODO just for debug
        if user_id is None:
            print("not login user,use default user 1 for test.")
            user_id = 1

        serializer.save(owner=WalletUser.objects.get(id=user_id))

    def list(self, request, *args, **kwargs):
        """
        query product by keyword
        """
        params = request.query_params
        keyword = params.get('keyword')
        if keyword is not None:
            print("keyword is ", keyword)
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
