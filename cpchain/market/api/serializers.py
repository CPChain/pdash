from django.utils import timezone
from rest_framework import serializers

from .models import Product, WalletUser, Token


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = (
        'id', 'owner_address', 'title', 'description', 'tags', 'price',
        'created', 'start_date', 'end_date', 'seq','file_md5',
        'signature','msg_hash')

    def create(self, validated_data):
        now = timezone.now()
        product = Product(
            owner_address=validated_data['owner_address'],
            title=validated_data['title'],
            description=validated_data['description'],
            price=validated_data['price'],
            created=now,
            start_date=validated_data['start_date'],
            end_date=validated_data['end_date'],
            signature=validated_data['signature'],
            owner=validated_data['owner'],
            file_md5=validated_data['file_md5'],
            seq=validated_data['seq'],
            msg_hash=validated_data['msg_hash'],
            tags=validated_data['tags'],
        )
        # TODO change to other algorithm.verify signature
        product.save()
        return product

    def update(self, instance, validated_data):
        print("update product status")
        status = validated_data['status']
        print("status:" + status)
        pass


class ProductUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ('owner_address', 'signature', 'status')

    def update(self, instance, validated_data):
        """
        Update and return an existing `Product` instance, given the validated data.
        """
        instance.status = validated_data.get('status', instance.status)
        instance.save()
        return instance


class UserRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = WalletUser
        fields = ('public_key', 'created')


class UserSerializer(serializers.ModelSerializer):
    product_set = serializers.PrimaryKeyRelatedField(many=True, queryset=Product.objects.all())

    class Meta:
        model = WalletUser
        fields = ('public_key', 'created', 'product_set')


class TokenSerializer(serializers.ModelSerializer):

    class Meta:
        model = Token
        fields = ('public_key', 'key')

