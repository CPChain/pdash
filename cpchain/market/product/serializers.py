from django.utils import timezone
from rest_framework import serializers
from .models import Product, WalletUser, SalesQuantity
from rest_framework_elasticsearch.es_serializer import ElasticModelSerializer
from .search_indexes import ProductIndex


class RecommendProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = (
            'id', 'owner_address', 'title', 'description', 'tags', 'price',
            'created', 'seq', 'file_md5',
            'signature', 'msg_hash')



class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = (
            'id', 'owner_address', 'title', 'description', 'tags', 'price',
            'created', 'start_date', 'end_date', 'seq', 'file_md5',
            'signature', 'msg_hash', 'status')

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
        product.save()
        product.indexing()
        return product


class ProductUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ('status',)

    def update(self, instance, validated_data):
        """
        Update and return an existing `Product` instance, given the validated data.
        """
        instance.status = validated_data.get('status', instance.status)
        instance.save()
        return instance


class ProductSalesQuantitySerializer(serializers.ModelSerializer):
    class Meta:
        model = SalesQuantity
        fields = ('quantity','market_hash')

    def update(self, instance, validated_data):
        instance.quantity += 1
        instance.save()
        return instance


class ElasticProductSerializer(ElasticModelSerializer):
    class Meta:
        model = Product
        es_model = ProductIndex
        fields = ('pk', 'owner_address', 'title', 'description', 'tags', 'price',
                  'created', 'start_date', 'end_date', 'seq', 'file_md5',
                  'signature', 'msg_hash', 'status')

