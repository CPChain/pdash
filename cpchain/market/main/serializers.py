import logging

from rest_framework import serializers

from .models import Carousel, HotTag, Promotion

logger = logging.getLogger(__name__)


class CarouselQuerySerializer(serializers.ModelSerializer):
    class Meta:
        model = Carousel
        fields = ('image','link')


class CarouselAddSerializer(serializers.ModelSerializer):
    class Meta:
        model = Carousel
        fields = ('name', 'image', 'link')


class HotTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = HotTag
        fields = ('image','tag')


class PromotionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Promotion
        fields = ('image','link')
