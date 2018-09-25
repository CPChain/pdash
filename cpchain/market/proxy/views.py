from rest_framework import viewsets, mixins
from rest_framework.response import Response

from cpchain.market.product.serializers import Product, ProductSerializer

class ProxyViewSet(mixins.ListModelMixin,
                   viewsets.GenericViewSet):

    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def list(self, request):
        data = [
            {
                "host": "127.0.0.1",
                "port": 5080
            },
            {
                "host": "127.0.0.1",
                "port": 5081
            },
            {
                "host": "127.0.0.1",
                "port": 5082
            }
        ]
        return Response(data=data)
