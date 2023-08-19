from rest_framework import serializers


class AudioFileSerializer(serializers.Serializer):
    audio_file = serializers.FileField()
    name = serializers.CharField()
    tg_id = serializers.CharField()


class BuySerializer(serializers.Serializer):
    merchant_id = serializers.CharField()
    amount = serializers.CharField()
    currency = serializers.CharField()
    callback_url = serializers.CharField()
    description = serializers.CharField()