from rest_framework.serializers import Serializer, ImageField, SerializerMethodField, ModelSerializer
from collections import OrderedDict
from .models import Image, Thumbnail
from pprint import pprint


class UploadSerializer(Serializer):
    file_uploaded = ImageField()

    class Meta:
        fields = ['file_uploaded']


class ImageSerializer(ModelSerializer):
    url = SerializerMethodField()
    details = SerializerMethodField()

    class Meta:
        model = Image
        fields = ['name', 'details', 'url']

    def get_url(self, image):
        if image.url == '':
            return None
        url = image.url.url
        request = self.context.get('request')
        return request.build_absolute_uri(url)

    def get_details(self, image):
        if not self.context.get('details'):
            return None
        request = self.context.get('request')
        return request.build_absolute_uri('/images/' + image.name)

    def to_representation(self, instance):
        result = super(ImageSerializer, self).to_representation(instance)
        return OrderedDict([(key, result[key]) for key in result if result[key] is not None])


class ImageWithThumbnailsSerializer(ImageSerializer):
    thumbnails = SerializerMethodField()

    class Meta:
        model = Image
        fields = ['name', 'url', 'thumbnails']

    def get_thumbnails(self, image):
        pprint(self.__dict__)
        request = self.context.get('request')
        thumbnails = Thumbnail.objects.filter(image=image)
        thumbnails_serializer = ThumbnailSerialzer(thumbnails, many=True, context={'request': request})
        return thumbnails_serializer.data


class ThumbnailSerialzer(ModelSerializer):
    url = SerializerMethodField()

    class Meta:
        model = Thumbnail
        fields = ['name', 'size', 'url']

    def get_url(self, thumbnail):
        url = thumbnail.url.url
        request = self.context.get('request')
        return request.build_absolute_uri(url)

