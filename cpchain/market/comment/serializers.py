from rest_framework import serializers

from .models import SummaryComment, Comment


class SummaryCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = SummaryComment
        fields = ('market_hash', 'avg_rating')


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ('public_key', 'market_hash', 'content', 'rating', 'created')
