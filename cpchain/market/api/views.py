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


PUBLIC_KEY = "public_key"


class UserLoginAPIView(APIView):
    """
    API endpoint that used to login.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        data = request.data
        public_key = data.get(PUBLIC_KEY)
        password = data.get('password')
        user = User.objects.get(public_key__exact= public_key)
        if user.password == password:
            serializer = UserSerializer(user)
            new_data = serializer.data
            # set userid ins session
            self.request.session['user_id'] = user.id
            return Response(new_data, status= HTTP_200_OK)
        return Response('password error', HTTP_400_BAD_REQUEST)


class UserRegisterAPIView(APIView):
    """
    API endpoint that used to register user account.
    """
    queryset = User.objects.all()
    serializer_class = UserRegisterSerializer
    permission_classes = (AllowAny,)

    def post(self, request):
        data = request.data
        public_key = data.get(PUBLIC_KEY)
        if User.objects.filter(public_key__exact=public_key):
            return Response("public_key already exists!", HTTP_400_BAD_REQUEST)
        serializer = UserRegisterSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
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
    def post(self):
        if self.request.session['user_id'] is not None:
            self.request.session['user_id'] = None
            return Response({"message": "logout success"}, status= HTTP_200_OK)
        else:
            return Response({"message": "not login"}, status= HTTP_400_BAD_REQUEST)


class ProductViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows query products.
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = (AllowAny,)
    # permission_classes = (IsOwnerOrReadOnly,)

    def perform_create(self, serializer):
        # user_id = self.request.session.get('user_id')
        # print('userId:' + user_id)
        # if user_id is None:
        #     print("userId is none")
        #     user_id = 1
        #     print('user_id:', user_id)

        serializer.save(owner=User.objects.get(id=1))


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows Products to be viewed by anyone.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
