from django.test import TestCase
from django.contrib.auth.models import User
from ..models import Image, AccountTier, AccountTierClass, ThumbnailSize, STATIC_URL


class ImageTestCase(TestCase):
    def setUp(self):
        self.thumbnails = [ThumbnailSize.get_or_create_validated(size) for size in [100, 200, 400, 800]]
        self.tier_class = AccountTierClass.get_or_create_validated(name='Basic', thumbnail_sizes=self.thumbnails)
        self.user = User(username='User', password='Password')
        self.user.save()
        self.account_tier = AccountTier.add_user_to_account_tier(tier=self.tier_class, user=self.user)

    def test_create_image(self):
        image = Image.create_image(self.user, '.jpg')
        self.assertEqual(Image.objects.count(), 1)
        self.assertTrue(image.name.endswith('.jpg'))
        self.assertTrue(image.name.startswith(str(self.user.pk)))
        self.assertIsNone(image.url)

    def test_create_multiple_images(self):
        image = Image.create_image(self.user, '.jpg')
        self.assertEqual(Image.objects.count(), 1)
        self.assertTrue(image.name.endswith('.jpg'))
        self.assertTrue(image.name.startswith(str(self.user.pk)))
        self.assertIsNone(image.url)

        second_image = Image.create_image(self.user, '.jpg')
        self.assertEqual(Image.objects.count(), 2)
        self.assertTrue(second_image.name.endswith('.jpg'))
        self.assertTrue(second_image.name.startswith(str(self.user.pk)))
        self.assertIsNone(second_image.url)
        self.assertNotEqual(image.name, second_image.name)

    def test_create_image_with_original_image(self):
        self.tier_class.original_image = True
        self.tier_class.save()
        image = Image.create_image(self.user, '.jpg')
        self.assertEqual(Image.objects.count(), 1)
        self.assertTrue(image.name.endswith('.jpg'))
        self.assertTrue(image.name.startswith(str(self.user.pk)))
        self.assertEqual(image.url, STATIC_URL + image.name)

    def test_create_image_with_png_extension(self):
        image = Image.create_image(self.user, '.png')
        self.assertEqual(Image.objects.count(), 1)
        self.assertTrue(image.name.endswith('.png'))
        self.assertTrue(image.name.startswith(str(self.user.pk)))
        self.assertIsNone(image.url)

    def test_create_image_with_user_without_account_tier(self):
        self.tier_class.delete()
        self.assertRaises(AccountTier.DoesNotExist, Image.create_image, self.user, '.png')
        self.assertEqual(Image.objects.count(), 0)

    def test_create_image_with_not_jpg_or_png_as_extension(self):
        values = ['', ' ', '1', '0', '-1', 'text', 1, 1, 1.1, -1.1, True, False, None, list(), tuple(), dict(), set()]
        for value in values:
            if isinstance(value, str):
                self.assertRaises(ValueError, Image.create_image, self.user, value)
            else:
                self.assertRaises(TypeError, Image.create_image, self.user, value)
        self.assertEqual(Image.objects.count(), 0)

    def test_create_image_with_not_user_as_owner(self):
        values = ['', ' ', '1', '0', '-1', 'text', 1, 1, 1.1, -1.1, True, False, None, list(), tuple(), dict(), set()]
        for value in values:
            self.assertRaises(TypeError, Image.create_image, value, '.jpg')
        self.assertEqual(Image.objects.count(), 0)