from django.forms import PasswordInput
from rest_framework import serializers
from collections import OrderedDict
from .models import Image, Thumbnail, ExpiringLink


class UploadSerializer(serializers.Serializer):
    file_uploaded = serializers.ImageField()

    class Meta:
        fields = ['file_uploaded']


class ImageSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()
    details = serializers.SerializerMethodField()

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
        request = self.context.get('request')
        return request.build_absolute_uri('/images/details/' + image.name)

    def to_representation(self, instance):
        result = super(ImageSerializer, self).to_representation(instance)
        return OrderedDict([(key, result[key]) for key in result if result[key] is not None])


class ImageWithThumbnailsSerializer(ImageSerializer):
    thumbnails = serializers.SerializerMethodField()

    class Meta:
        model = Image
        fields = ['name', 'url', 'thumbnails']

    def get_thumbnails(self, image):
        request = self.context.get('request')
        thumbnails = Thumbnail.objects.filter(image=image)
        thumbnails_serializer = ThumbnailSerialzer(thumbnails, many=True, context={'request': request})
        return thumbnails_serializer.data


class ThumbnailSerialzer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()

    class Meta:
        model = Thumbnail
        fields = ['name', 'size', 'url']

    def get_url(self, thumbnail):
        url = thumbnail.url.url
        request = self.context.get('request')
        return request.build_absolute_uri(url)


class LinkGeneratorSerilaizer(serializers.Serializer):
    image_name = serializers.CharField()
    seconds = serializers.IntegerField()

    class Meta:
        fields = ['image_name', 'seconds']


class ExpiringLinkSerializer(serializers.ModelSerializer):
    expiring_time = serializers.DateTimeField(format="%H:%M:%S %d.%m.%y")
    url = serializers.SerializerMethodField()

    class Meta:
        model = ExpiringLink
        fields = ['url', 'expiring_time']

    def get_url(self, expiring_link):
        request = self.context.get('request')
        return request.build_absolute_uri(expiring_link.name)


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    class Meta:
        fields = ['username', 'password']
