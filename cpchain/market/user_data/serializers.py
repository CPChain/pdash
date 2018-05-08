from django.utils import timezone
from rest_framework import serializers

from .models import UploadFileInfo, BuyerFileInfo, UserInfoVersion, ProductTag, Bookmark
import logging

logger = logging.getLogger(__name__)


class UploadFileInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = UploadFileInfo
        fields = (
            'id','public_key', 'name', 'hashcode', 'path', 'size',
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
        )
        file_info.save()
        return file_info


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


class UserInfoVersionSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserInfoVersion
        fields = ('version',)


class ProductTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductTag
        fields = ('tag',)

    def create(self, validated_data):
        # check if the same tag exist
        tag_name = validated_data['tag']
        query_set = ProductTag.objects.filter(tag=tag_name)
        if query_set:
            logging.debug("existing the same tag:%s" % tag_name )
            return query_set[0]

        t = ProductTag(
            tag=tag_name,
        )
        t.save()
        return t


class BookmarkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bookmark
        fields = ('market_hash','name','public_key','created,')

    def create(self, validated_data):
        bookmark = Bookmark(
            market_hash=validated_data['market_hash'],
            name = validated_data['name'],
            public_key=validated_data['public_key'],
        )
        bookmark.save()
        return bookmark
