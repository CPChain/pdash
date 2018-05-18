from rest_framework import serializers

from cpchain.market.product.models import Product
from cpchain.market.account.models import WalletUser, Token


class UserRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = WalletUser
        fields = ('public_key', 'created', 'address')


class UserSerializer(serializers.ModelSerializer):
    product_set = serializers.PrimaryKeyRelatedField(many=True, queryset=Product.objects.all())

    class Meta:
        model = WalletUser
        fields = ('public_key', 'created', 'product_set')


class TokenSerializer(serializers.ModelSerializer):

    class Meta:
        model = Token
        fields = ('public_key', 'key')

