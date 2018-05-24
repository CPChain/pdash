from django.utils import timezone
from rest_framework import serializers

from .models import UploadFileInfo, BuyerFileInfo, UserInfoVersion, ProductTag, Bookmark
import logging

logger = logging.getLogger(__name__)


class UploadFileInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = UploadFileInfo
        fields = (
            'id','public_key', 'name', 'hashcode', 'path', 'size', 'client_id',
            'remote_type', 'remote_uri', 'is_published', 'aes_key', 'market_hash',
            'created')

    def create(self, validated_data):
        file_info = UploadFileInfo(
            public_key=validated_data['public_key'],
            name=validated_data['name'],
            hashcode=validated_data['hashcode'],
            path=validated_data['path'],
            size=validated_data['size'],
            remote_type=validated_data['remote_type'],
            is_published=validated_data['is_published'],
            aes_key=validated_data['aes_key'],
            market_hash=validated_data['market_hash'],
            client_id=validated_data['client_id'],
        )
        file_info.save()
        return file_info

    def update(self, instance, validated_data):
        instance.market_hash = validated_data['market_hash']
        instance.is_published = validated_data['is_published']
        instance.save()
        return instance


class BuyerFileInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = BuyerFileInfo
        fields = (
            'id','public_key', 'order_id', 'market_hash', 'file_uuid', 'file_title',
            'path', 'size', 'is_downloaded', 'created')

    def create(self, validated_data):
        file_info = BuyerFileInfo(
            public_key=validated_data['public_key'],
            order_id=validated_data['order_id'],
            market_hash=validated_data['market_hash'],
            file_uuid=validated_data['file_uuid'],
            file_title=validated_data['file_title'],
            path=validated_data['path'],
            size=validated_data['size'],
            is_downloaded=validated_data['is_downloaded'],
        )
        file_info.save()
        return file_info

    def update(self, instance, validated_data):
        instance.is_downloaded = validated_data['is_downloaded']
        instance.save()
        return instance


class BuyerFileInfoUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = BuyerFileInfo
        fields = ('order_id', 'is_downloaded')

    def update(self, instance, validated_data):
        instance.is_downloaded = validated_data['is_downloaded']
        instance.save()
        return instance


class UserInfoVersionSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserInfoVersion
        fields = ('version',)


class ProductTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductTag
        fields = ('tag',)

    def create(self, validated_data):
        obj, created = ProductTag.objects.get_or_create(**validated_data)
        return obj


class BookmarkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bookmark
        fields = ('market_hash','name','public_key','created')

    def create(self, validated_data):
        bookmark, created = Bookmark.objects.get_or_create(**validated_data)
        return bookmark
