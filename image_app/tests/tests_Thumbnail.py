from django.test import TestCase
from django.contrib.auth.models import User
from django.core.files import File
from PIL import Image as PILImage
import io
import os
from ..models import Thumbnail, Image, AccountTier, AccountTierClass, ThumbnailSize


class ThumbnailTestCase(TestCase):
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
        self.image = Image.create_image(self.user, self.file)

    def tearDown(self):
        ThumbnailSize.objects.all().delete()
        AccountTierClass.objects.all().delete()
        User.objects.all().delete()
        AccountTier.objects.all().delete()
        Image.objects.all().delete()
        Thumbnail.objects.all().delete()

    def Test_create_thumbnail(self):
        _, thumbnail = Thumbnail.create_thumbnail(image=self.image, thumbnail_size=self.thumbnails[0], file=self.file)
        self.assertIsInstance(thumbnail, Thumbnail)
        self.assertTrue(thumbnail.name.endswith(self.file.name[-4:]))
        self.assertEqual(thumbnail.url.name, 'thumbnails/' + thumbnail.name)
        self.assertEqual(Thumbnail.objects.count(), 1)
        self.assertEqual(Thumbnail.objects.filter(image__owner=self.user).count(), 1)
        os.remove('media/' + thumbnail.url.name)

    def Test_create_same_thumbnail_twice(self):
        _, thumbnail = Thumbnail.create_thumbnail(image=self.image, thumbnail_size=self.thumbnails[0], file=self.file)
        self.assertIsInstance(thumbnail, Thumbnail)
        self.assertTrue(thumbnail.name.endswith(self.file.name[-4:]))
        self.assertEqual(thumbnail.url.name, 'thumbnails/' + thumbnail.name)
        self.assertEqual(Thumbnail.objects.count(), 1)
        self.assertEqual(Thumbnail.objects.filter(image__owner=self.user).count(), 1)

        self.assertRaises(ValueError, Thumbnail.create_thumbnail, self.image, self.thumbnails[0], self.file)
        self.assertEqual(Thumbnail.objects.count(), 1)
        self.assertEqual(Thumbnail.objects.filter(image__owner=self.user).count(), 1)
        os.remove('media/' + thumbnail.url.name)

    def Test_create_different_thumbnail_size_to_same_image(self):
        _, thumbnail = Thumbnail.create_thumbnail(image=self.image, thumbnail_size=self.thumbnails[0], file=self.file)
        self.assertIsInstance(thumbnail, Thumbnail)
        self.assertTrue(thumbnail.name.endswith(self.file.name[-4:]))
        self.assertEqual(thumbnail.url.name, 'thumbnails/' + thumbnail.name)
        self.assertEqual(Thumbnail.objects.count(), 1)
        self.assertEqual(Thumbnail.objects.filter(image__owner=self.user).count(), 1)

        _, second_thumbnail = Thumbnail.create_thumbnail(image=self.image, thumbnail_size=self.thumbnails[1],
                                                         file=self.file)
        self.assertIsInstance(second_thumbnail, Thumbnail)
        self.assertTrue(thumbnail.name.endswith(self.file.name[-4:]))
        self.assertEqual(second_thumbnail.url.name, 'thumbnails/' + second_thumbnail.name)
        self.assertNotEqual(second_thumbnail.name, thumbnail.name)
        self.assertEqual(Thumbnail.objects.count(), 2)
        self.assertEqual(Thumbnail.objects.filter(image__owner=self.user).count(), 2)
        os.remove('media/' + thumbnail.url.name)
        os.remove('media/' + second_thumbnail.url.name)

    def Test_create_thumbnail_with_thumbnail_size_that_is_not_in_users_account_tier(self):
        self.tier_class.thumbnail_sizes.remove(self.thumbnails[0])
        self.assertRaises(ValueError, Thumbnail.create_thumbnail, self.image, self.thumbnails[0], self.file)
        self.assertEqual(Thumbnail.objects.count(), 0)
        self.assertEqual(Thumbnail.objects.filter(image__owner=self.user).count(), 0)

    def test_create_thumbnail_with_not_image_as_image(self):
        values = ['', ' ', '1', '0', '-1', 'text', 1, 1, 1.1, -1.1, True, False, None, list(), tuple(), dict(), set()]
        for value in values:
            self.assertRaises(TypeError, Thumbnail.create_thumbnail, value, self.thumbnails[0], self.file)
        self.assertEqual(Thumbnail.objects.count(), 0)

    def test_create_thumbnail_with_not_thumbnail_size_as_thumbnail_size(self):
        values = ['', ' ', '1', '0', '-1', 'text', 1, 1, 1.1, -1.1, True, False, None, list(), tuple(), dict(), set()]
        for value in values:
            self.assertRaises(TypeError, Thumbnail.create_thumbnail, self.image, value, self.file)
        self.assertEqual(Thumbnail.objects.count(), 0)

    def test_create_thumbnail_with_not_file_as_file(self):
        values = ['', ' ', '1', '0', '-1', 'text', 1, 1, 1.1, -1.1, True, False, None, list(), tuple(), dict(), set()]
        for value in values:
            self.assertRaises(TypeError, Thumbnail.create_thumbnail, self.image, self.thumbnails[0], value)
        self.assertEqual(Thumbnail.objects.count(), 0)

    def test_in_order(self):
        self.Test_create_thumbnail()
        self.tearDown()
        self.setUp()
        self.Test_create_same_thumbnail_twice()
        self.tearDown()
        self.setUp()
        self.Test_create_different_thumbnail_size_to_same_image()
        self.tearDown()
        self.setUp()
        self.Test_create_thumbnail_with_thumbnail_size_that_is_not_in_users_account_tier()
        self.tearDown()
