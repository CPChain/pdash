from django.utils import timezone
from rest_framework import serializers

from .models import Product, WalletUser
from .utils import md5


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ('id', 'owner_address', 'title', 'description', 'price', 'created', 'expired_date', 'verify_code')

    def create(self, validated_data):
        now = timezone.now()
        product = Product(
            owner_address=validated_data['owner_address'],
            title=validated_data['title'],
            description=validated_data['description'],
            price=validated_data['price'],
            created=now,
            owner=validated_data['owner'],
        )
        # TODO change to other algorithm.
        # hash(product.title,product.description)
        verify_code = md5("".join([product.owner_address, product.description]).encode("utf-8"))
        print(verify_code)
        product.verify_code = verify_code
        product.save()
        return product


class UserRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = WalletUser
        fields = ('public_key', 'created')


class UserSerializer(serializers.ModelSerializer):
    product_set = serializers.PrimaryKeyRelatedField(many=True, queryset=Product.objects.all())

    class Meta:
        model = WalletUser
        fields = ('public_key', 'created', 'product_set')
