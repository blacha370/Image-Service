from rest_framework.test import APITestCase, APIRequestFactory
from django.contrib.auth.models import User, AnonymousUser
from django.utils import timezone
from django.core.files.uploadedfile import SimpleUploadedFile
from datetime import timedelta
from PIL import Image as PILImage
import io
import os
from ..views import GetImage
from ..models import ThumbnailSize, AccountTierClass, AccountTier, Image, ExpiringLink


class GetImageTestCase(APITestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.view = GetImage.as_view()
        self.user = User(username='test', password='test')
        self.user.save()
        self.thumbnail_size = ThumbnailSize.get_or_create_validated(200)
        self.account_tier_class = AccountTierClass.get_or_create_validated(name='Basic',
                                                                           thumbnail_sizes=[self.thumbnail_size],
                                                                           original_image=True, expiring_link=True)
        AccountTier.add_user_to_account_tier(self.account_tier_class, self.user)
        img = PILImage.new('RGB', (1000, 1000), color='red')
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='jpeg')
        self.file = SimpleUploadedFile('uploaded_file.jpg', img_bytes.getvalue(), content_type='image/jpeg')

    def test_get_image(self):
        image = Image.create_image(self.user, self.file)
        link = ExpiringLink.generate(image, 300)
        request = self.factory.get('link/')
        request.user = AnonymousUser
        response = self.view(request, link.name).get('content-type')
        self.assertEqual(response, 'image/jpeg')

        img = PILImage.new('RGB', (1000, 1000), color='red')
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='jpeg')
        self.file = SimpleUploadedFile('uploaded_file.png', img_bytes.getvalue(), content_type='image/png')
        second_image = Image.create_image(self.user, self.file)
        link = ExpiringLink.generate(second_image, 300)
        response = self.view(request, link.name).get('content-type')
        self.assertEqual(response, 'image/png')
        os.remove('media/' + image.url.name)
        os.remove('media/' + second_image.url.name)

    def test_get_image_with_wrong_name(self):
        image = Image.create_image(self.user, self.file)
        request = self.factory.get('link/')
        request.user = AnonymousUser
        response = self.view(request, 'image.jpg')
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data['message'], 'Resource not found')
        os.remove('media/' + image.url.name)

    def test_get_image_with_expired_link(self):
        image = Image.create_image(self.user, self.file)
        link = ExpiringLink.generate(image, 300)
        link.expiring_time = timezone.now() - timedelta(seconds=5)
        link.save()
        request = self.factory.get('link/')
        request.user = AnonymousUser
        response = self.view(request, link.name)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data['message'], 'Resource not found')
        os.remove('media/' + image.url.name)

    def test_get_image_with_not_string_as_image_name(self):
        image = Image.create_image(self.user, self.file)
        link = ExpiringLink.generate(image, 300)
        values = [1, 0, -1, 1.1, -1.1, True, False, None, list(), tuple(), dict(), set()]
        for value in values:
            request = self.factory.get('link/')
            request.user = AnonymousUser
            response = self.view(request, value)
            self.assertEqual(response.status_code, 404)
            self.assertEqual(response.data['message'], 'Resource not found')
        os.remove('media/' + image.url.name)
