from django.test import TestCase
from django.contrib.auth.models import User
from django.core.files import File
from PIL import Image as PILImage
import io
import os
from ..models import Image, AccountTier, AccountTierClass, ThumbnailSize, ExpiringLink


class ExpiringLinkTestCase(TestCase):
    def setUp(self):
        self.thumbnails = [ThumbnailSize.get_or_create_validated(size) for size in [100, 200, 400, 800]]
        self.tier_class = AccountTierClass.get_or_create_validated(name='Basic', thumbnail_sizes=self.thumbnails,
                                                                   original_image=True)
        self.user = User(username='User', password='Password')
        self.user.save()
        self.account_tier = AccountTier.add_user_to_account_tier(tier=self.tier_class, user=self.user)
        img = PILImage.new('RGB', (1000, 1000), color='red')
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='jpeg')
        self.file = File(img_bytes, name='uploaded_file.jpg')
        self.image = Image.create_image(self.user, file=self.file)

    def test_generate_expiring_link(self):
        link = ExpiringLink.generate(self.image, 400)
        self.assertIsInstance(link, ExpiringLink)
        self.assertIn(self.image.name, link.name)
        self.assertEqual(ExpiringLink.objects.count(), 1)
        self.assertEqual(ExpiringLink.objects.filter(image=self.image).count(), 1)
        os.remove('media/' + self.image.url.name)

    def test_generate_multiple_expiring_links_to_same_image(self):
        link = ExpiringLink.generate(self.image, 400)
        self.assertIsInstance(link, ExpiringLink)
        self.assertIn(self.image.name, link.name)
        self.assertEqual(ExpiringLink.objects.count(), 1)
        self.assertEqual(ExpiringLink.objects.filter(image=self.image).count(), 1)

        link = ExpiringLink.generate(self.image, 400)
        self.assertIsInstance(link, ExpiringLink)
        self.assertIn(self.image.name, link.name)
        self.assertEqual(ExpiringLink.objects.count(), 2)
        self.assertEqual(ExpiringLink.objects.filter(image=self.image).count(), 2)
        os.remove('media/' + self.image.url.name)

    def test_generate_expiring_link_with_wrong_int_as_seconds(self):
        self.assertRaises(ValueError, ExpiringLink.generate, self.image, -1)
        self.assertRaises(ValueError, ExpiringLink.generate, self.image, 0)
        self.assertRaises(ValueError, ExpiringLink.generate, self.image, 299)
        self.assertRaises(ValueError, ExpiringLink.generate, self.image, 30001)
        self.assertEqual(ExpiringLink.objects.count(), 0)
        os.remove('media/' + self.image.url.name)

    def test_generate_expiring_link_with_not_image_as_image(self):
        values = ['', ' ', '1', '0', '-1', 'text', 1, 1, 1.1, -1.1, True, False, None, list(), tuple(), dict(), set()]
        for value in values:
            self.assertRaises(TypeError, ExpiringLink.generate, value, 400)
        self.assertEqual(ExpiringLink.objects.count(), 0)
        os.remove('media/' + self.image.url.name)

    def test_generate_expiring_link_with_not_int_as_seconds(self):
        values = ['', ' ', '1', '0', '-1', 'text', 301.1, 1.1, -1.1, True, False, None, list(), tuple(), dict(), set()]
        for value in values:
            self.assertRaises(TypeError, ExpiringLink.generate, self.image, value)
        self.assertEqual(ExpiringLink.objects.count(), 0)
        os.remove('media/' + self.image.url.name)
