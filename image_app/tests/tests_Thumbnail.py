from django.test import TestCase
from django.contrib.auth.models import User
from ..models import Thumbnail, Image, AccountTier, AccountTierClass, ThumbnailSize, STATIC_URL


class ThumbnailTestCase(TestCase):
    def setUp(self):
        self.thumbnails = [ThumbnailSize.get_or_create_validated(size) for size in [100, 200, 400, 800]]
        self.tier_class = AccountTierClass.get_or_create_validated(name='Basic', thumbnail_sizes=self.thumbnails)
        self.user = User(username='User', password='Password')
        self.user.save()
        self.account_tier = AccountTier.add_user_to_account_tier(tier=self.tier_class, user=self.user)
        self.image = Image.create_image(self.user, '.jpg')

    def test_create_thumbnail(self):
        thumbnail = Thumbnail.create_thumbnail(image=self.image, thumbnail_size=self.thumbnails[0])
        self.assertEqual(Thumbnail.objects.count(), 1)
        self.assertEqual(thumbnail.image, self.image)
        self.assertEqual(thumbnail.thumbnail_size, self.thumbnails[0])
        self.assertEqual(thumbnail.name, self.image.name.replace('.jpg', '_' + str(self.thumbnails[0].height) + '.jpg'))
        self.assertEqual(thumbnail.url, STATIC_URL + thumbnail.name)

    def test_create_same_thumbnail_twice(self):
        thumbnail = Thumbnail.create_thumbnail(image=self.image, thumbnail_size=self.thumbnails[0])
        self.assertEqual(Thumbnail.objects.count(), 1)
        self.assertEqual(thumbnail.image, self.image)
        self.assertEqual(thumbnail.thumbnail_size, self.thumbnails[0])
        self.assertEqual(thumbnail.name, self.image.name.replace('.jpg', '_' + str(self.thumbnails[0].height) + '.jpg'))
        self.assertEqual(thumbnail.url, STATIC_URL + thumbnail.name)

        self.assertRaises(ValueError, Thumbnail.create_thumbnail, self.image, self.thumbnails[0])

    def test_create_different_thumbnail_size_to_same_image(self):
        thumbnail = Thumbnail.create_thumbnail(image=self.image, thumbnail_size=self.thumbnails[0])
        self.assertEqual(Thumbnail.objects.count(), 1)
        self.assertEqual(thumbnail.image, self.image)
        self.assertEqual(thumbnail.thumbnail_size, self.thumbnails[0])
        self.assertEqual(thumbnail.name, self.image.name.replace('.jpg', '_' + str(self.thumbnails[0].height) + '.jpg'))
        self.assertEqual(thumbnail.url, STATIC_URL + thumbnail.name)

        thumbnail = Thumbnail.create_thumbnail(image=self.image, thumbnail_size=self.thumbnails[1])
        self.assertEqual(Thumbnail.objects.count(), 2)
        self.assertEqual(thumbnail.image, self.image)
        self.assertEqual(thumbnail.thumbnail_size, self.thumbnails[1])
        self.assertEqual(thumbnail.name, self.image.name.replace('.jpg', '_' + str(self.thumbnails[1].height) + '.jpg'))
        self.assertEqual(thumbnail.url, STATIC_URL + thumbnail.name)

    def test_create_thumbnail_with_thumbnail_size_that_is_not_in_users_account_tier(self):
        self.tier_class.thumbnail_sizes.remove(self.thumbnails[0])
        self.assertRaises(ValueError, Thumbnail.create_thumbnail, self.image, self.thumbnails[0])
        self.assertEqual(Thumbnail.objects.count(), 0)

    def test_create_thumbnail_with_not_image_as_image(self):
        values = ['', ' ', '1', '0', '-1', 'text', 1, 1, 1.1, -1.1, True, False, None, list(), tuple(), dict(), set()]
        for value in values:
            self.assertRaises(TypeError, Thumbnail.create_thumbnail, value, self.thumbnails[0])
        self.assertEqual(Thumbnail.objects.count(), 0)

    def test_create_thumbnail_with_not_thumbnail_size_as_thumbnail_size(self):
        values = ['', ' ', '1', '0', '-1', 'text', 1, 1, 1.1, -1.1, True, False, None, list(), tuple(), dict(), set()]
        for value in values:
            self.assertRaises(TypeError, Thumbnail.create_thumbnail, self.image, value)
        self.assertEqual(Thumbnail.objects.count(), 0)
