from django.test import TestCase
from django.contrib.auth.models import User
from ..models import AccountTier, AccountTierClass, ThumbnailSize


class AccountTierTestCase(TestCase):
    def setUp(self):
        self.thumbnails = [ThumbnailSize.get_or_create_validated(size) for size in [100, 200, 400, 800]]
        self.tier_class = AccountTierClass.get_or_create_validated(name='Basic', thumbnail_sizes=self.thumbnails)
        self.user = User(username='User', password='Password')
        self.user.save()

    def test_add_user_to_account_tier(self):
        account_tier = AccountTier.add_user_to_account_tier(tier=self.tier_class, user=self.user)
        self.assertEqual(AccountTier.objects.count(), 1)
        self.assertEqual(account_tier.user, self.user)
        self.assertEqual(account_tier.tier, self.tier_class)

    def test_add_user_to_same_account_tier_multiple_times(self):
        account_tier = AccountTier.add_user_to_account_tier(tier=self.tier_class, user=self.user)
        self.assertEqual(AccountTier.objects.count(), 1)
        self.assertEqual(account_tier.user, self.user)
        self.assertEqual(account_tier.tier, self.tier_class)

        self.assertRaises(ValueError, AccountTier.add_user_to_account_tier, self.tier_class, self.user)
        self.assertEqual(AccountTier.objects.count(), 1)

    def test_add_user_to_multiple_account_tiers(self):
        account_tier = AccountTier.add_user_to_account_tier(tier=self.tier_class, user=self.user)
        self.assertEqual(AccountTier.objects.count(), 1)
        self.assertEqual(account_tier.user, self.user)
        self.assertEqual(account_tier.tier, self.tier_class)

        second_tier_class = AccountTierClass.get_or_create_validated(name='Pro', thumbnail_sizes=self.thumbnails[:-1])
        self.assertRaises(ValueError, AccountTier.add_user_to_account_tier, second_tier_class, self.user)
        self.assertEqual(AccountTier.objects.count(), 1)

    def test_add_different_users_to_same_account_tier(self):
        account_tier = AccountTier.add_user_to_account_tier(tier=self.tier_class, user=self.user)
        self.assertEqual(AccountTier.objects.count(), 1)
        self.assertEqual(account_tier.user, self.user)
        self.assertEqual(account_tier.tier, self.tier_class)

        second_user = User(username='Second_User', password='Password')
        second_user.save()
        account_tier = AccountTier.add_user_to_account_tier(tier=self.tier_class, user=second_user)
        self.assertEqual(AccountTier.objects.count(), 2)
        self.assertEqual(account_tier.user, second_user)
        self.assertEqual(account_tier.tier, self.tier_class)

    def test_add_different_users_to_different_account_tiers(self):
        account_tier = AccountTier.add_user_to_account_tier(tier=self.tier_class, user=self.user)
        self.assertEqual(AccountTier.objects.count(), 1)
        self.assertEqual(account_tier.user, self.user)
        self.assertEqual(account_tier.tier, self.tier_class)

        second_tier_class = AccountTierClass.get_or_create_validated(name='Pro', thumbnail_sizes=self.thumbnails[:-1])
        second_user = User(username='Second_User', password='Password')
        second_user.save()
        account_tier = AccountTier.add_user_to_account_tier(tier=second_tier_class, user=second_user)
        self.assertEqual(AccountTier.objects.count(), 2)
        self.assertEqual(account_tier.user, second_user)
        self.assertEqual(account_tier.tier, second_tier_class)

    def test_add_user_to_account_tier_with_not_user_as_user(self):
        values = ['', ' ', '1', '0', '-1', 'text', 1, 1, 1.1, -1.1, True, False, None, list(), tuple(), dict(), set()]
        for value in values:
            self.assertRaises(TypeError, AccountTier.add_user_to_account_tier, self.tier_class, value)
        self.assertEqual(AccountTier.objects.count(), 0)

    def test_add_user_to_account_tier_with_not_account_tier_class_as_tier(self):
        values = ['', ' ', '1', '0', '-1', 'text', 1, 1, 1.1, -1.1, True, False, None, list(), tuple(), dict(), set()]
        for value in values:
            self.assertRaises(TypeError, AccountTier.add_user_to_account_tier, value, self.user)
        self.assertEqual(AccountTier.objects.count(), 0)

    def test_change_account_tier(self):
        account_tier = AccountTier.add_user_to_account_tier(tier=self.tier_class, user=self.user)
        second_tier_class = AccountTierClass.get_or_create_validated(name='Pro', thumbnail_sizes=self.thumbnails[:-1])
        self.assertEqual(AccountTier.objects.count(), 1)
        account_tier.change_account_tier(second_tier_class)
        self.assertEqual(AccountTier.objects.count(), 1)
        self.assertEqual(account_tier.tier, second_tier_class)
        self.assertEqual(account_tier.user, self.user)

    def test_change_account_tier_to_same_tier(self):
        account_tier = AccountTier.add_user_to_account_tier(tier=self.tier_class, user=self.user)
        self.assertEqual(AccountTier.objects.count(), 1)
        self.assertRaises(ValueError, account_tier.change_account_tier, self.tier_class)
        self.assertEqual(AccountTier.objects.count(), 1)
        self.assertEqual(account_tier.tier, self.tier_class)
        self.assertEqual(account_tier.user, self.user)

    def test_change_account_tier_with_not_account_tier_class_as_tier(self):
        account_tier = AccountTier.add_user_to_account_tier(tier=self.tier_class, user=self.user)
        self.assertEqual(AccountTier.objects.count(), 1)
        values = ['', ' ', '1', '0', '-1', 'text', 1, 1, 1.1, -1.1, True, False, None, list(), tuple(), dict(), set()]
        for value in values:
            self.assertRaises(TypeError, account_tier.change_account_tier, value)
        self.assertEqual(AccountTier.objects.count(), 1)
        account_tier = AccountTier.objects.get(user=self.user)
        self.assertEqual(account_tier.tier, self.tier_class)
