from rest_framework.serializers import Serializer, ImageField, ModelSerializer
from .models import Image, Thumbnail


class UploadSerializer(Serializer):
    file_uploaded = ImageField()

    class Meta:
        fields = ['file_uploaded']


class ImageSerializer(ModelSerializer):
    class Meta:
        model = Image
        fields = ['url', 'name']


class ThumbnailSerialzer(ModelSerializer):
    class Meta:
        model = Thumbnail
        fields = ['url', 'name', 'size']

