from rest_framework.serializers import Serializer, ImageField, ModelSerializer
from collections import OrderedDict
from .models import Image, Thumbnail


class UploadSerializer(Serializer):
    file_uploaded = ImageField()

    class Meta:
        fields = ['file_uploaded']


class ImageSerializer(ModelSerializer):
    class Meta:
        model = Image
        fields = ['url', 'name']

    def to_representation(self, instance):
        result = super(ImageSerializer, self).to_representation(instance)
        return OrderedDict([(key, result[key]) for key in result if result[key] is not None])


class ThumbnailSerialzer(ModelSerializer):
    class Meta:
        model = Thumbnail
        fields = ['url', 'name', 'size']

