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

# class ElasticProductSerializer(ElasticModelSerializer):
#     class Meta:
#         model = Product
#         es_model = ProductIndex
#         fields = ('pk', 'owner_address', 'title', 'description', 'tags', 'price',
#                   'created', 'start_date', 'end_date', 'seq', 'file_md5',
#                   'signature', 'msg_hash', 'status')

