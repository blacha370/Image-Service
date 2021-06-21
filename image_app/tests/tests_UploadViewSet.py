from rest_framework.test import APITestCase, APIRequestFactory, force_authenticate
from django.contrib.auth.models import User
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

    def test_create_upload_image(self):
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
