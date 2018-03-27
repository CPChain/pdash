# accept public key from client(wallet),
# response string with encrypted(random string)
# if client decrypt correctly ,login success
# else response with HTTP_400_BAD_REQUEST
from django.http import JsonResponse
from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from rest_framework.views import APIView

from .permissions import IsOwnerOrReadOnly
from .serializers import *


# login
class UserLoginAPIView(APIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        data = request.data
        public_key = data.get('username')
        password = data.get('password')
        user = User.objects.get(username__exact=public_key)
        if user.password == password:
            serializer = UserSerializer(user)
            new_data = serializer.data
            # set userid ins session
            self.request.session['user_id'] = user.id
            return Response(new_data, status=HTTP_200_OK)
        return Response('password error', HTTP_400_BAD_REQUEST)


# 用于注册
class UserRegisterAPIView(APIView):
    queryset = User.objects.all()
    serializer_class = UserRegisterSerializer
    permission_classes = (AllowAny,)

    def post(self, request):
        data = request.data
        public_key = data.get("public_key")
        if User.objects.filter(public_key__exact=public_key):
            return Response("user name already exists!",HTTP_400_BAD_REQUEST)
        serializer = UserRegisterSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            # return Response(serializer.data, status=HTTP_200_OK)
            d = {
                'status': 1,
                'message': 'success',
            }
            return JsonResponse(d)
        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)


class LogoutAPIView(APIView):
    def post(self):
        if self.request.session['user_id'] is not None:
            self.request.session['user_id'] = None
            return Response({"message":"登出成功"}, status=HTTP_200_OK)
        else:
            return Response({"message":"暂未登陆，无需登出"}, status=HTTP_400_BAD_REQUEST)


# query products
class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = (IsOwnerOrReadOnly,)

    def perform_create(self, serializer):
        serializer.save(owner=User.objects.get(id=self.request.session.get('user_id')))


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
