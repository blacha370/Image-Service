from django.contrib.auth.mixins import LoginRequiredMixin
from rest_framework.viewsets import ViewSet
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import UploadSerializer, ImageSerializer, ImageWithThumbnailsSerializer
from .models import Image, AccountTier, Thumbnail


class UploadViewSet(LoginRequiredMixin, ViewSet):
    serializer_class = UploadSerializer

    def create(self, request):
        file_uploaded = request.FILES.get('file_uploaded')
        if file_uploaded is None:
            return Response({'message': 'Image not send'}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        elif file_uploaded.content_type == 'image/jpeg' or file_uploaded.content_type == 'image/png':
            try:
                account_tier = AccountTier.objects.get(user=request.user).tier
                img = Image.create_image(owner=request.user, file=file_uploaded)
                thumbnail_sizes = account_tier.thumbnail_sizes.order_by('-height')
                for thumbnail_size in thumbnail_sizes:
                    file_uploaded, thumbnail = Thumbnail.create_thumbnail(image=img, thumbnail_size=thumbnail_size,
                                                                          file=file_uploaded)
                image = ImageWithThumbnailsSerializer(img, context={'request': request})
                return Response(image.data)
            except AccountTier.DoesNotExist:
                return Response({'message': 'Not allowed to upload images'}, status=status.HTTP_403_FORBIDDEN)
        return Response({'message': 'Unsupported media type. Valid media types: "image/jpeg", "image/png"'},
                        status=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)


class ListImages(LoginRequiredMixin, APIView):
    def get(self, request):
        images = Image.objects.filter(owner=request.user)
        images_serializer = ImageSerializer(images, many=True, context={'request': request, 'details': True})
        return Response(images_serializer.data)


class ImageDetails(LoginRequiredMixin, APIView):
    def get(self, request, image_name):
        if isinstance(image_name, str) and (image_name.endswith('.jpg') or image_name.endswith('.png')):
            try:
                image = Image.objects.get(owner=request.user, name=image_name)
                image = ImageWithThumbnailsSerializer(image, context={'request': request})
                return Response(image.data)
            except Image.DoesNotExist:
                return Response({'message': 'Image does not exists'}, status=status.HTTP_404_NOT_FOUND)
        return Response({'message': 'Image name is not valid'}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
