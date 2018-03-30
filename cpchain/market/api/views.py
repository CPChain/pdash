# accept public key from client(wallet),
# response string with encrypted(random string)
# if client decrypt correctly ,login success
# else response with HTTP_400_BAD_REQUEST
from django.db.models import Q
from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from rest_framework.views import APIView

from .permissions import IsOwnerOrReadOnly
from .serializers import *
from .models import Product
from rest_framework.authtoken.models import Token

PUBLIC_KEY = "public_key"


class UserLoginAPIView(APIView):
    """
    API endpoint that used to login.
    """
    queryset = WalletUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        data = request.data
        public_key = data.get(PUBLIC_KEY)
        password = data.get('password')
        user = WalletUser.objects.get(public_key__exact= public_key)
        if user.password == password:
            serializer = UserSerializer(user)
            new_data = serializer.data

            token = Token.objects.create(user=user)
            print(token.key)
            # set userid ins session
            self.request.session['user_id'] = user.id
            return Response(new_data, status= HTTP_200_OK)
        return Response('password error', HTTP_400_BAD_REQUEST)


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
            user_in_db = WalletUser.objects.get(public_key__exact=public_key)
            token = Token.objects.create(user=user_in_db)
            print(token.key)
            # return Response(serializer.data, status=HTTP_200_OK)
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
        print("logout")
        user_id = request._request.session['user_id']

        # user_id = self.request.session['user_id']
        # print("user_id:" + user_id)
        # # return Response({"message": "not login"}, status=HTTP_400_BAD_REQUEST)
        # if user_id is not None:
        #     self.request.session['user_id'] = None
        #     return Response({"message": "logout success"}, status= HTTP_200_OK)
        # else:
        #     return Response({"message": "not login"}, status= HTTP_400_BAD_REQUEST)
        return Response({"message": "not login"}, status= HTTP_400_BAD_REQUEST)


class ProductViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows query products.
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    # permission_classes = (AllowAny,)
    permission_classes = (IsOwnerOrReadOnly,)

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
