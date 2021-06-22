from django.test import TestCase
from ..models import AccountTierClass, ThumbnailSize


class AccountTierClassTestCase(TestCase):
    def setUp(self):
        self.thumbnails = [ThumbnailSize.get_or_create_validated(size) for size in [100, 200, 400, 800]]

    def test_create_account_tier_class(self):
        self.assertEqual(AccountTierClass.objects.count(), 0)
        account_tier_class = AccountTierClass.get_or_create_validated(name='Basic', thumbnail_sizes=self.thumbnails)
        self.assertEqual(AccountTierClass.objects.count(), 1)
        self.assertEqual(account_tier_class.name, 'Basic')
        self.assertEqual(account_tier_class.thumbnail_sizes.count(), len(self.thumbnails))
        self.assertFalse(account_tier_class.original_image)
        self.assertFalse(account_tier_class.expiring_link)

    def test_create_account_tier_class_with_same_name(self):
        self.assertEqual(AccountTierClass.objects.count(), 0)
        account_tier_class = AccountTierClass.get_or_create_validated(name='Basic', thumbnail_sizes=self.thumbnails)
        self.assertEqual(AccountTierClass.objects.count(), 1)
        self.assertEqual(account_tier_class.name, 'Basic')
        self.assertEqual(account_tier_class.thumbnail_sizes.count(), len(self.thumbnails))
        self.assertFalse(account_tier_class.original_image)
        self.assertFalse(account_tier_class.expiring_link)

        self.assertRaises(ValueError, AccountTierClass.get_or_create_validated, 'Basic', self.thumbnails[:-1])

    def test_create_account_tier_class_with_same_thumbnails_original_image_and_expiring_link(self):
        self.assertEqual(AccountTierClass.objects.count(), 0)
        account_tier_class = AccountTierClass.get_or_create_validated(name='Basic', thumbnail_sizes=self.thumbnails)
        self.assertEqual(AccountTierClass.objects.count(), 1)
        self.assertEqual(account_tier_class.name, 'Basic')
        self.assertEqual(account_tier_class.thumbnail_sizes.count(), len(self.thumbnails))
        self.assertFalse(account_tier_class.original_image)
        self.assertFalse(account_tier_class.expiring_link)

        self.assertRaises(ValueError, AccountTierClass.get_or_create_validated, 'Pro', self.thumbnails)

    def test_create_account_tier_class_with_same_thumbnails_and_original_image(self):
        self.assertEqual(AccountTierClass.objects.count(), 0)
        account_tier_class = AccountTierClass.get_or_create_validated(name='Basic', thumbnail_sizes=self.thumbnails,
                                                                      original_image=True)
        self.assertEqual(AccountTierClass.objects.count(), 1)
        self.assertEqual(account_tier_class.name, 'Basic')
        self.assertEqual(account_tier_class.thumbnail_sizes.count(), len(self.thumbnails))
        self.assertTrue(account_tier_class.original_image)
        self.assertFalse(account_tier_class.expiring_link)

        account_tier_class = AccountTierClass.get_or_create_validated(name='Pro', thumbnail_sizes=self.thumbnails,
                                                                      original_image=True, expiring_link=True)
        self.assertEqual(AccountTierClass.objects.count(), 2)
        self.assertEqual(account_tier_class.name, 'Pro')
        self.assertEqual(account_tier_class.thumbnail_sizes.count(), len(self.thumbnails))
        self.assertTrue(account_tier_class.original_image)
        self.assertTrue(account_tier_class.expiring_link)

    def test_create_account_tier_class_with_same_thumbnails_and_expiring_link(self):
        self.assertEqual(AccountTierClass.objects.count(), 0)
        account_tier_class = AccountTierClass.get_or_create_validated(name='Basic', thumbnail_sizes=self.thumbnails)
        self.assertEqual(AccountTierClass.objects.count(), 1)
        self.assertEqual(account_tier_class.name, 'Basic')
        self.assertEqual(account_tier_class.thumbnail_sizes.count(), len(self.thumbnails))
        self.assertFalse(account_tier_class.original_image)
        self.assertFalse(account_tier_class.expiring_link)

        account_tier_class = AccountTierClass.get_or_create_validated(name='Pro', thumbnail_sizes=self.thumbnails,
                                                                      original_image=True)
        self.assertEqual(AccountTierClass.objects.count(), 2)
        self.assertEqual(account_tier_class.name, 'Pro')
        self.assertEqual(account_tier_class.thumbnail_sizes.count(), len(self.thumbnails))
        self.assertTrue(account_tier_class.original_image)
        self.assertFalse(account_tier_class.expiring_link)

    def test_create_account_tier_class_with_same_thumbnails(self):
        self.assertEqual(AccountTierClass.objects.count(), 0)
        account_tier_class = AccountTierClass.get_or_create_validated(name='Basic', thumbnail_sizes=self.thumbnails)
        self.assertEqual(AccountTierClass.objects.count(), 1)
        self.assertEqual(account_tier_class.name, 'Basic')
        self.assertEqual(account_tier_class.thumbnail_sizes.count(), len(self.thumbnails))
        self.assertFalse(account_tier_class.original_image)
        self.assertFalse(account_tier_class.expiring_link)

        account_tier_class = AccountTierClass.get_or_create_validated(name='Pro', thumbnail_sizes=self.thumbnails,
                                                                      original_image=True, expiring_link=True)
        self.assertEqual(AccountTierClass.objects.count(), 2)
        self.assertEqual(account_tier_class.name, 'Pro')
        self.assertEqual(account_tier_class.thumbnail_sizes.count(), len(self.thumbnails))
        self.assertTrue(account_tier_class.original_image)
        self.assertTrue(account_tier_class.expiring_link)

    def test_create_account_tier_class_with_same_original_image_and_expiring_link(self):
        self.assertEqual(AccountTierClass.objects.count(), 0)
        account_tier_class = AccountTierClass.get_or_create_validated(name='Basic', thumbnail_sizes=self.thumbnails)
        self.assertEqual(AccountTierClass.objects.count(), 1)
        self.assertEqual(account_tier_class.name, 'Basic')
        self.assertEqual(account_tier_class.thumbnail_sizes.count(), len(self.thumbnails))
        self.assertFalse(account_tier_class.original_image)
        self.assertFalse(account_tier_class.expiring_link)

        account_tier_class = AccountTierClass.get_or_create_validated(name='Pro', thumbnail_sizes=self.thumbnails[:-1])
        self.assertEqual(AccountTierClass.objects.count(), 2)
        self.assertEqual(account_tier_class.name, 'Pro')
        self.assertEqual(account_tier_class.thumbnail_sizes.count(), len(self.thumbnails) - 1)
        self.assertFalse(account_tier_class.original_image)
        self.assertFalse(account_tier_class.expiring_link)

    def test_create_account_tier_class_with_same_original_image(self):
        self.assertEqual(AccountTierClass.objects.count(), 0)
        account_tier_class = AccountTierClass.get_or_create_validated(name='Basic', thumbnail_sizes=self.thumbnails)
        self.assertEqual(AccountTierClass.objects.count(), 1)
        self.assertEqual(account_tier_class.name, 'Basic')
        self.assertEqual(account_tier_class.thumbnail_sizes.count(), len(self.thumbnails))
        self.assertFalse(account_tier_class.original_image)
        self.assertFalse(account_tier_class.expiring_link)

        account_tier_class = AccountTierClass.get_or_create_validated(name='Pro', thumbnail_sizes=self.thumbnails[:-1],
                                                                      expiring_link=True)
        self.assertEqual(AccountTierClass.objects.count(), 2)
        self.assertEqual(account_tier_class.name, 'Pro')
        self.assertEqual(account_tier_class.thumbnail_sizes.count(), len(self.thumbnails) - 1)
        self.assertFalse(account_tier_class.original_image)
        self.assertFalse(account_tier_class.expiring_link)

    def test_create_account_tier_class_with_same_expiring_link(self):
        self.assertEqual(AccountTierClass.objects.count(), 0)
        account_tier_class = AccountTierClass.get_or_create_validated(name='Basic', thumbnail_sizes=self.thumbnails)
        self.assertEqual(AccountTierClass.objects.count(), 1)
        self.assertEqual(account_tier_class.name, 'Basic')
        self.assertEqual(account_tier_class.thumbnail_sizes.count(), len(self.thumbnails))
        self.assertFalse(account_tier_class.original_image)
        self.assertFalse(account_tier_class.expiring_link)

        account_tier_class = AccountTierClass.get_or_create_validated(name='Pro', thumbnail_sizes=self.thumbnails[:-1],
                                                                      original_image=True)
        self.assertEqual(AccountTierClass.objects.count(), 2)
        self.assertEqual(account_tier_class.name, 'Pro')
        self.assertEqual(account_tier_class.thumbnail_sizes.count(), len(self.thumbnails) - 1)
        self.assertTrue(account_tier_class.original_image)
        self.assertFalse(account_tier_class.expiring_link)

    def test_create_account_tier_class_with_different_data(self):
        self.assertEqual(AccountTierClass.objects.count(), 0)
        account_tier_class = AccountTierClass.get_or_create_validated(name='Basic', thumbnail_sizes=self.thumbnails)
        self.assertEqual(AccountTierClass.objects.count(), 1)
        self.assertEqual(account_tier_class.name, 'Basic')
        self.assertEqual(account_tier_class.thumbnail_sizes.count(), len(self.thumbnails))
        self.assertFalse(account_tier_class.original_image)
        self.assertFalse(account_tier_class.expiring_link)

        account_tier_class = AccountTierClass.get_or_create_validated(name='Pro', thumbnail_sizes=self.thumbnails[:-1],
                                                                      original_image=True, expiring_link=True)
        self.assertEqual(AccountTierClass.objects.count(), 2)
        self.assertEqual(account_tier_class.name, 'Pro')
        self.assertEqual(account_tier_class.thumbnail_sizes.count(), len(self.thumbnails) - 1)
        self.assertTrue(account_tier_class.original_image)
        self.assertTrue(account_tier_class.expiring_link)

    def test_create_account_tier_class_with_not_string_as_name(self):
        values = [1, 1, 1.1, -1.1, True, False, None, list(), tuple(), dict(), set()]
        for value in values:
            self.assertRaises(TypeError, AccountTierClass.get_or_create_validated, value, self.thumbnails)
        self.assertEqual(AccountTierClass.objects.count(), 0)

    def test_create_account_tier_class_with_not_list_of_thumbnail_sizes_as_thumbnail_sizes(self):
        values = [1, 1, 1.1, -1.1, True, False, None, list(), tuple(), dict(), set()]
        for value in values:
            self.assertRaises(TypeError, AccountTierClass.get_or_create_validated, 'Basic', value)
        self.assertEqual(AccountTierClass.objects.count(), 0)

    def test_create_account_tier_with_not_bool_as_original_image(self):
        values = ['', ' ', '1', '0', '-1', 'text', 1, 1, 1.1, -1.1, None, list(), tuple(), dict(), set()]
        for value in values:
            self.assertRaises(TypeError, AccountTierClass.get_or_create_validated, 'Basic', self.thumbnails, value)
        self.assertEqual(AccountTierClass.objects.count(), 0)

    def test_create_account_tier_with_not_bool_as_expiring_link(self):
        values = ['', ' ', '1', '0', '-1', 'text', 1, 1, 1.1, -1.1, None, list(), tuple(), dict(), set()]
        for value in values:
            self.assertRaises(TypeError, AccountTierClass.get_or_create_validated, 'Basic', self.thumbnails, False,
                              value)
        self.assertEqual(AccountTierClass.objects.count(), 0)