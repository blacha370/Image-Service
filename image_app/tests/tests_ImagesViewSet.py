from rest_framework.test import APITestCase, APIRequestFactory, force_authenticate
from django.contrib.auth.models import User, AnonymousUser
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image as PILImage
import io
from ..views import ImagesViewSet
from ..models import ThumbnailSize, AccountTierClass, AccountTier, Image


def create_image():
    img = PILImage.new('RGB', (1000, 1000), color='red')
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='jpeg')
    return SimpleUploadedFile('uploaded_file.jpg', img_bytes.getvalue(), content_type='image/jpeg')


class ImagesViewSetTestCase(APITestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.view = ImagesViewSet.as_view({'get': 'get'})
        self.user = User(username='test', password='test')
        self.user.save()
        self.thumbnail_size = ThumbnailSize.get_or_create_validated(200)
        self.account_tier_class = AccountTierClass.get_or_create_validated(name='Basic',
                                                                           thumbnail_sizes=[self.thumbnail_size])
        AccountTier.add_user_to_account_tier(self.account_tier_class, self.user)

    def test_without_images(self):
        request = self.factory.get('images/')
        force_authenticate(request, self.user)
        request.user = self.user
        response = self.view(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [])

    def test_with_images(self):
        for i in range(20):
            Image.create_image(self.user, create_image())
        request = self.factory.get('images/')
        force_authenticate(request, self.user)
        request.user = self.user
        response = self.view(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), Image.objects.count())

    def test_with_other_user_images(self):
        for i in range(20):
            Image.create_image(self.user, create_image())
        user = User(username='test1', password='test1')
        user.save()
        request = self.factory.get('images/')
        force_authenticate(request, user)
        request.user = user
        response = self.view(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), Image.objects.filter(owner=user).count())
        self.assertEqual(Image.objects.count(), 20)

    def test_with_both_other_user_images_and_own(self):
        for i in range(20):
            Image.create_image(self.user, create_image())
        user = User(username='test1', password='test1')
        user.save()
        AccountTier.add_user_to_account_tier(self.account_tier_class, user)
        for i in range(10):
            Image.create_image(user, create_image())
        request = self.factory.get('images/')
        force_authenticate(request, user)
        request.user = user
        response = self.view(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), Image.objects.filter(owner=user).count())
        self.assertEqual(Image.objects.count(), 30)

    def test_without_authentication(self):
        request = self.factory.get('images/')
        request.user = AnonymousUser()
        response = self.view(request)
        self.assertEqual(response.status_code, 302)
