from rest_framework.test import APITestCase, APIRequestFactory, force_authenticate
from django.contrib.auth.models import User, AnonymousUser
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image as PILImage
import io
import os
from ..views import UploadViewSet
from ..models import ThumbnailSize, AccountTierClass, AccountTier, Thumbnail, Image


class UploadViewSetTestCase(APITestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.view = UploadViewSet.as_view({'post': 'create'})
        self.user = User(username='test', password='test')
        self.user.save()
        self.thumbnail_sizes = [ThumbnailSize.get_or_create_validated(size) for size in [200, 400]]
        self.account_tier_classes = [
            AccountTierClass.get_or_create_validated(name='Basic', thumbnail_sizes=self.thumbnail_sizes[:1]),
            AccountTierClass.get_or_create_validated(name='Pro', thumbnail_sizes=self.thumbnail_sizes,
                                                     original_image=True),
            AccountTierClass.get_or_create_validated(name='Enterprise', thumbnail_sizes=self.thumbnail_sizes,
                                                     original_image=True, expiring_link=True)
        ]
        img = PILImage.new('RGB', (1000, 1000), color='red')
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='jpeg')
        self.file = SimpleUploadedFile('uploaded_file.jpg', img_bytes.getvalue(), content_type='image/jpeg')

    def test_upload_image(self):
        AccountTier.add_user_to_account_tier(self.account_tier_classes[0], self.user)
        request = self.factory.post('upload/', {'file_uploaded': self.file})
        force_authenticate(request, self.user)
        request.user = self.user
        response = self.view(request)
        self.assertEqual(Image.objects.count(), 1)
        self.assertEqual(Image.objects.filter(owner=self.user).count(), 1)
        self.assertEqual(Thumbnail.objects.count(), 1)
        self.assertEqual(Thumbnail.objects.filter(image__owner=self.user).count(), 1)
        image = Image.objects.get(pk=1)
        thumbnail = Thumbnail.objects.get(pk=1)
        self.assertEqual(response.data['name'], image.name)
        self.assertEqual(response.data['thumbnails'][0]['name'], thumbnail.name)
        self.assertEqual(response.data['thumbnails'][0]['size'], '200px')
        os.remove('media/' + thumbnail.url.name)

    def test_upload_image_with_original_image(self):
        AccountTier.add_user_to_account_tier(self.account_tier_classes[1], self.user)
        request = self.factory.post('upload/', {'file_uploaded': self.file})
        force_authenticate(request, self.user)
        request.user = self.user
        response = self.view(request)
        self.assertEqual(Image.objects.count(), 1)
        self.assertEqual(Image.objects.filter(owner=self.user).count(), 1)
        self.assertEqual(Thumbnail.objects.count(), 2)
        self.assertEqual(Thumbnail.objects.filter(image__owner=self.user).count(), 2)
        image = Image.objects.get(pk=1)
        thumbnail = Thumbnail.objects.all()
        self.assertEqual(response.data['name'], image.name)
        self.assertEqual(response.data['thumbnails'][0]['name'], thumbnail[0].name)
        self.assertEqual(response.data['thumbnails'][0]['size'], '400px')
        self.assertEqual(response.data['thumbnails'][1]['name'], thumbnail[1].name)
        self.assertEqual(response.data['thumbnails'][1]['size'], '200px')
        os.remove('media/' + thumbnail[0].url.name)
        os.remove('media/' + thumbnail[1].url.name)
        os.remove('media/' + image.url.name)

    def test_create_without_file(self):
        AccountTier.add_user_to_account_tier(self.account_tier_classes[0], self.user)
        request = self.factory.post('upload/')
        force_authenticate(request, self.user)
        request.user = self.user
        response = self.view(request)
        self.assertEqual(response.data['message'], 'Image not send')
        self.assertEqual(Image.objects.count(), 0)
        self.assertEqual(Image.objects.filter(owner=self.user).count(), 0)
        self.assertEqual(Thumbnail.objects.count(), 0)
        self.assertEqual(Thumbnail.objects.filter(image__owner=self.user).count(), 0)

    def test_upload_image_without_authentication(self):
        AccountTier.add_user_to_account_tier(self.account_tier_classes[0], self.user)
        request = self.factory.post('upload/', {'file_uploaded': self.file})
        request.user = AnonymousUser()
        response = self.view(request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/login?next=/upload')
        self.assertEqual(Image.objects.count(), 0)
        self.assertEqual(Image.objects.filter(owner=self.user).count(), 0)
        self.assertEqual(Thumbnail.objects.count(), 0)
        self.assertEqual(Thumbnail.objects.filter(image__owner=self.user).count(), 0)

    def test_upload_second_image(self):
        AccountTier.add_user_to_account_tier(self.account_tier_classes[0], self.user)
        request = self.factory.post('upload/', {'file_uploaded': self.file})
        force_authenticate(request, self.user)
        request.user = self.user
        response = self.view(request)
        self.assertEqual(Image.objects.count(), 1)
        self.assertEqual(Image.objects.filter(owner=self.user).count(), 1)
        self.assertEqual(Thumbnail.objects.count(), 1)
        self.assertEqual(Thumbnail.objects.filter(image__owner=self.user).count(), 1)
        image = Image.objects.get(pk=1)
        thumbnail = Thumbnail.objects.get(pk=1)
        self.assertEqual(response.data['name'], image.name)
        self.assertEqual(response.data['thumbnails'][0]['name'], thumbnail.name)
        self.assertEqual(response.data['thumbnails'][0]['size'], '200px')
        os.remove('media/' + thumbnail.url.name)

        img = PILImage.new('RGB', (1000, 1000), color='red')
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='jpeg')
        file = SimpleUploadedFile('uploaded_file.jpg', img_bytes.getvalue(), content_type='image/jpeg')
        request = self.factory.post('upload/', {'file_uploaded': file})
        force_authenticate(request, self.user)
        request.user = self.user
        response = self.view(request)
        self.assertEqual(Image.objects.count(), 2)
        self.assertEqual(Image.objects.filter(owner=self.user).count(), 2)
        self.assertEqual(Thumbnail.objects.count(), 2)
        self.assertEqual(Thumbnail.objects.filter(image__owner=self.user).count(), 2)
        image = Image.objects.get(pk=2)
        thumbnail = Thumbnail.objects.get(pk=2)
        self.assertEqual(response.data['name'], image.name)
        self.assertEqual(response.data['thumbnails'][0]['name'], thumbnail.name)
        self.assertEqual(response.data['thumbnails'][0]['size'], '200px')
        os.remove('media/' + thumbnail.url.name)

    def test_upload_png_image(self):
        self.file.name = 'uploaded_file.png'
        AccountTier.add_user_to_account_tier(self.account_tier_classes[0], self.user)
        request = self.factory.post('upload/', {'file_uploaded': self.file})
        force_authenticate(request, self.user)
        request.user = self.user
        response = self.view(request)
        self.assertEqual(Image.objects.count(), 1)
        self.assertEqual(Image.objects.filter(owner=self.user).count(), 1)
        self.assertEqual(Thumbnail.objects.count(), 1)
        self.assertEqual(Thumbnail.objects.filter(image__owner=self.user).count(), 1)
        image = Image.objects.get(pk=1)
        thumbnail = Thumbnail.objects.get(pk=1)
        self.assertEqual(response.data['name'], image.name)
        self.assertEqual(response.data['thumbnails'][0]['name'], thumbnail.name)
        self.assertEqual(response.data['thumbnails'][0]['size'], '200px')
        os.remove('media/' + thumbnail.url.name)

    def test_upload_image_with_no_png_or_jpg_extension(self):
        self.file.name = 'uploaded_file.jpeg'
        AccountTier.add_user_to_account_tier(self.account_tier_classes[0], self.user)
        request = self.factory.post('upload/', {'file_uploaded': self.file})
        force_authenticate(request, self.user)
        request.user = self.user
        response = self.view(request)
        self.assertEqual(response.status_code, 422)
        self.assertEqual(response.data['message'], 'Not supported file extension. Supported extensions: .jpg, .png')
        self.assertEqual(Image.objects.count(), 0)
        self.assertEqual(Image.objects.filter(owner=self.user).count(), 0)
        self.assertEqual(Thumbnail.objects.count(), 0)
        self.assertEqual(Thumbnail.objects.filter(image__owner=self.user).count(), 0)
