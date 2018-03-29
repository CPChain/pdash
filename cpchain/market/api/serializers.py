import hashlib

from .models import Product, User
from rest_framework import serializers
import datetime
from django.utils import timezone


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ('id', 'owner_address', 'title', 'description', 'price', 'created_date', 'expired_date', 'verify_code')

    def create(self, validated_data):
        now = timezone.now()
        product = Product(
            owner_address=validated_data['owner_address'],
            title=validated_data['title'],
            description=validated_data['description'],
            price=validated_data['price'],
            created_date=now,
            expired_date=now,
            owner=validated_data['owner'],
        )
        # hash(product.title,product.description)
        verify_code = md5("".join([product.owner_address, product.description]).encode("utf-8"))
        print(verify_code)
        product.verify_code = verify_code
        product.save()
        return product


def md5(source):
    digest = hashlib.md5()
    digest.update(source)
    return digest.hexdigest()


class UserRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('public_key', 'date_of_birth')


class UserSerializer(serializers.ModelSerializer):
    product_set = serializers.PrimaryKeyRelatedField(many=True, queryset=Product.objects.all())

    class Meta:
        model = User
        fields = ('public_key', 'date_of_birth', 'product_set')
