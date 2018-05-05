from django.utils import timezone
from rest_framework import serializers

from .models import UploadFileInfo, BuyerFileInfo, UserInfoVersion


class UploadFileInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = UploadFileInfo
        fields = (
            'id', 'public_key', 'name', 'hashcode', 'path', 'size',
            'remote_type', 'remote_uri', 'is_published', 'aes_key', 'market_hash',
            'created')

    def create(self, validated_data):
        file_info = UploadFileInfo(
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
            'id', 'public_key', 'order_id', 'market_hash', 'file_uuid', 'file_title',
            'path', 'size', 'is_downloaded', 'created')

    def create(self, validated_data):
        now = timezone.now()
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
