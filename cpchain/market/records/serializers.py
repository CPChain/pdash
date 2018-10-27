from rest_framework import serializers

from .models import Record, Config


class RecordSerializer(serializers.ModelSerializer):

    class Meta:
        model = Record
        fields = '__all__'

class ConfigSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Config
        fields = '__all__'
