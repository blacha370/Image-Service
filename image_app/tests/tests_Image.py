from django.test import TestCase
from django.contrib.auth.models import User
from django.core.files import File
from PIL import Image as PILImage
import io
import os
from ..models import Image, AccountTier, AccountTierClass, ThumbnailSize


class ImageTestCase(TestCase):
    def setUp(self):
        self.thumbnails = [ThumbnailSize.get_or_create_validated(size) for size in [100, 200, 400, 800]]
        self.tier_class = AccountTierClass.get_or_create_validated(name='Basic', thumbnail_sizes=self.thumbnails)
        self.user = User(username='User', password='Password')
        self.user.save()
        self.account_tier = AccountTier.add_user_to_account_tier(tier=self.tier_class, user=self.user)
        img = PILImage.new('RGB', (1000, 1000), color='red')
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='jpeg')
        self.file = File(img_bytes, name='uploaded_file.jpg')

    def test_create_image(self):
        image = Image.create_image(owner=self.user, file=self.file)
        self.assertIsInstance(image, Image)
        self.assertTrue(image.name.endswith(self.file.name[-4:]))
        self.assertEqual(image.url.name, '')
        self.assertEqual(Image.objects.count(), 1)
        self.assertEqual(Image.objects.filter(owner=self.user).count(), 1)

    def test_create_multiple_images(self):
        image = Image.create_image(owner=self.user, file=self.file)
        self.assertIsInstance(image, Image)
        self.assertTrue(image.name.endswith(self.file.name[-4:]))
        self.assertEqual(image.url.name, '')
        self.assertEqual(Image.objects.count(), 1)
        self.assertEqual(Image.objects.filter(owner=self.user).count(), 1)

        second_image = Image.create_image(owner=self.user, file=self.file)
        self.assertIsInstance(second_image, Image)
        self.assertTrue(second_image.name.endswith(self.file.name[-4:]))
        self.assertNotEqual(second_image.name, image.name)
        self.assertEqual(second_image.url.name, '')
        self.assertEqual(Image.objects.count(), 2)
        self.assertEqual(Image.objects.filter(owner=self.user).count(), 2)

    def test_create_image_with_original_image(self):
        self.tier_class.original_image = True
        self.tier_class.save()
        image = Image.create_image(owner=self.user, file=self.file)
        self.assertIsInstance(image, Image)
        self.assertTrue(image.name.endswith(self.file.name[-4:]))
        self.assertEqual(image.url.name, 'images/' + image.name)
        self.assertEqual(Image.objects.count(), 1)
        self.assertEqual(Image.objects.filter(owner=self.user).count(), 1)
        os.remove('media/' + image.url.name)

    def test_create_image_with_png_extension(self):
        img = PILImage.new('RGB', (1000, 1000), color='red')
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='jpeg')
        self.file = File(img_bytes, name='uploaded_file.png')
        image = Image.create_image(owner=self.user, file=self.file)
        self.assertIsInstance(image, Image)
        self.assertTrue(image.name.endswith(self.file.name[-4:]))
        self.assertEqual(image.url.name, '')
        self.assertEqual(Image.objects.count(), 1)
        self.assertEqual(Image.objects.filter(owner=self.user).count(), 1)

    def test_create_image_with_user_without_account_tier(self):
        self.account_tier.delete()
        self.assertRaises(AccountTier.DoesNotExist, Image.create_image, self.user, self.file)
        self.assertEqual(Image.objects.count(), 0)
        self.assertEqual(Image.objects.filter(owner=self.user).count(), 0)

    def test_create_image_with_not_jpg_or_png_extension(self):
        img = PILImage.new('RGB', (1000, 1000), color='red')
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='jpeg')
        self.file = File(img_bytes, name='uploaded_file.jpeg')
        self.assertRaises(ValueError, Image.create_image, self.user, self.file)

    def test_create_image_with_not_user_as_owner(self):
        values = ['', ' ', '1', '0', '-1', 'text', 1, 1, 1.1, -1.1, True, False, None, list(), tuple(), dict(), set()]
        for value in values:
            self.assertRaises(TypeError, Image.create_image, value, self.file)
        self.assertEqual(Image.objects.count(), 0)

    def test_create_image_with_not_file_as_file(self):
        values = ['', ' ', '1', '0', '-1', 'text', 1, 1, 1.1, -1.1, True, False, None, list(), tuple(), dict(), set()]
        for value in values:
            self.assertRaises(TypeError, Image.create_image, self.user, value)
        self.assertEqual(Image.objects.count(), 0)
