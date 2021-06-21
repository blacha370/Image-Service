from django.contrib.auth.mixins import LoginRequiredMixin
from django.http.response import HttpResponse
from rest_framework.viewsets import ViewSet, ReadOnlyModelViewSet
from rest_framework.decorators import action
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime
from .serializers import *
from .models import Image, AccountTier, Thumbnail, ExpiringLink


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
                return Response(image.data, status=status.HTTP_201_CREATED)
            except AccountTier.DoesNotExist:
                return Response({'message': 'Not allowed to upload images'}, status=status.HTTP_403_FORBIDDEN)
        return Response({'message': 'Unsupported media type. Valid media types: "image/jpeg", "image/png"'},
                        status=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)


class ImagesViewSet(LoginRequiredMixin, ReadOnlyModelViewSet):
    serializer_class = ImageSerializer
    queryset = Image.objects.all().order_by('-pk')

    def get(self, request):
        images = self.queryset.filter(owner=self.request.user)
        serializer = ImageSerializer(images, many=True, context={'request': request})
        return Response(serializer.data)


class ImagesWithDetailsViewSet(LoginRequiredMixin, ReadOnlyModelViewSet):
    serializer_class = ImageWithThumbnailsSerializer
    queryset = Image.objects.all().order_by('-pk')

    def get(self, request):
        images = self.queryset.filter(owner=request.user)
        serializer = self.get_serializer(images, context={'request': request}, many=True)
        return Response(serializer.data)

    @action(detail=False)
    def get_one(self, request, image_name):
        if isinstance(image_name, str) and (image_name.endswith('.jpg') or image_name.endswith('.png')):
            try:
                image = self.queryset.get(owner=request.user, name=image_name)
                serializer = self.get_serializer(image, context={'request': request})
                return Response(serializer.data)
            except Image.DoesNotExist:
                return Response({'message': 'Image does not exists'}, status=status.HTTP_404_NOT_FOUND)
        return Response({'message': 'Image name is not valid'}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)


class GenerateExpiringLink(LoginRequiredMixin, ViewSet):
    serializer_class = LinkGeneratorSerilaizer

    def create(self, request):
        try:
            image = Image.objects.get(owner=request.user, name=request.data['image_name'])
            link = ExpiringLink.generate(image, int(request.data['seconds']))
            link = ExpiringLinkSerializer(link, context={'request': request})
            return Response(link.data)
        except Image.DoesNotExist:
            return Response({'message': 'Image does not exists'}, status=status.HTTP_404_NOT_FOUND)
        except ValueError:
            return Response({'message': 'Not valid arguments'}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)


class GetImage(APIView):
    def get(self, request, expiring_name):
        try:
            link = ExpiringLink.objects.get(name=expiring_name, expiring_time__gte=datetime.now())
            if link.image.name.endswith('.jpg'):
                return HttpResponse(link.image.url.read(), content_type='image/jpeg')
            elif link.image.name.endswith('.jpg'):
                return HttpResponse(link.image.url.read(), content_type='image/png')
            else:
                return Response({'message': 'Unsupported media type'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except (ExpiringLink.DoesNotExist, FileNotFoundError):
            return Response({'message': 'Resource not found'}, status=status.HTTP_404_NOT_FOUND)
