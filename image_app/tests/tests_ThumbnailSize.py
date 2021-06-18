from django.test import TestCase
from ..models import ThumbnailSize


class ThumbnailSizeTestCase(TestCase):
    def test_get_or_create(self):
        self.assertEqual(ThumbnailSize.objects.count(), 0)
        size = ThumbnailSize.get_or_create_validated(100)
        self.assertEqual(ThumbnailSize.objects.count(), 1)
        self.assertEqual(size.height, 100)

    def test_get_or_create_multiple_times_with_same_value(self):
        self.assertEqual(ThumbnailSize.objects.count(), 0)
        ThumbnailSize.get_or_create_validated(100)
        self.assertEqual(ThumbnailSize.objects.count(), 1)
        ThumbnailSize.get_or_create_validated(100)
        self.assertEqual(ThumbnailSize.objects.count(), 1)

    def test_get_or_create_with_0_as_height(self):
        self.assertRaises(ValueError, ThumbnailSize.get_or_create_validated, 0)
        self.assertEqual(ThumbnailSize.objects.count(), 0)

    def test_get_or_create_with_negative_int_as_height(self):
        self.assertRaises(ValueError, ThumbnailSize.get_or_create_validated, -1)
        self.assertEqual(ThumbnailSize.objects.count(), 0)

    def test_get_or_create_with_not_int_as_height(self):
        values = ['', ' ', '1', '0', '-1', 'text', 1.1, -1.1, True, False, None, list(), tuple(), dict(), set()]
        for value in values:
            self.assertRaises(TypeError, ThumbnailSize.get_or_create_validated, value)
        self.assertEqual(ThumbnailSize.objects.count(), 0)
