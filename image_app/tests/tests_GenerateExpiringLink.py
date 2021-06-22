from rest_framework.test import APITestCase, APIRequestFactory, force_authenticate
from django.contrib.auth.models import User, AnonymousUser
from django.core.files.uploadedfile import SimpleUploadedFile
from datetime import datetime
from PIL import Image as PILImage
import io
import os
from ..views import GenerateExpiringLink
from ..models import ThumbnailSize, AccountTierClass, AccountTier, Image, ExpiringLink


class GenerateExpiringLinkTestCase(APITestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.view = GenerateExpiringLink.as_view({'post': 'create'})
        self.user = User(username='test', password='test')
        self.user.save()
        self.thumbnail_sizes = [ThumbnailSize.get_or_create_validated(size) for size in [200, 400]]
        self.account_tier_classes = [
            AccountTierClass.get_or_create_validated(name='Basic', thumbnail_sizes=self.thumbnail_sizes[:1]),
            AccountTierClass.get_or_create_validated(name='Pro', thumbnail_sizes=self.thumbnail_sizes,
                                                     original_image=True),
            AccountTierClass.get_or_create_validated(name='Enterprise', thumbnail_sizes=self.thumbnail_sizes,
                                                     original_image=True, expiring_link=True)
        ]
        img = PILImage.new('RGB', (1000, 1000), color='red')
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='jpeg')
        self.file = SimpleUploadedFile('uploaded_file.jpg', img_bytes.getvalue(), content_type='image/jpeg')

    def test_generate_expiring_link(self):
        AccountTier.add_user_to_account_tier(self.account_tier_classes[2], self.user)
        image = Image.create_image(self.user, self.file)
        request = self.factory.post('link/', {'image_name': image.name, 'seconds': 300}, format='json')
        force_authenticate(request, self.user)
        request.user = self.user
        response = self.view(request)
        self.assertEqual(ExpiringLink.objects.count(), 1)
        self.assertEqual(ExpiringLink.objects.filter(image=image).count(), 1)
        link = ExpiringLink.objects.get(image=image)
        self.assertIn(link.name, response.data['url'])
        self.assertEqual(datetime.strftime(link.expiring_time, "%H:%M:%S %d.%m.%y"), response.data['expiring_time'])
        os.remove('media/' + image.url.name)

    def test_generate_expiring_link_to_image_multiple_times(self):
        AccountTier.add_user_to_account_tier(self.account_tier_classes[2], self.user)
        image = Image.create_image(self.user, self.file)
        request = self.factory.post('link/', {'image_name': image.name, 'seconds': 300}, format='json')
        force_authenticate(request, self.user)
        request.user = self.user
        response = self.view(request)
        self.assertEqual(ExpiringLink.objects.count(), 1)
        self.assertEqual(ExpiringLink.objects.filter(image=image).count(), 1)
        link = ExpiringLink.objects.get(image=image)
        self.assertIn(link.name, response.data['url'])
        self.assertEqual(datetime.strftime(link.expiring_time, "%H:%M:%S %d.%m.%y"), response.data['expiring_time'])

        request = self.factory.post('link/', {'image_name': image.name, 'seconds': 300}, format='json')
        force_authenticate(request, self.user)
        request.user = self.user
        response = self.view(request)
        self.assertEqual(ExpiringLink.objects.count(), 2)
        self.assertEqual(ExpiringLink.objects.filter(image=image).count(), 2)
        link = ExpiringLink.objects.get(image=image, name=response.data['url'].split('/')[-1])
        self.assertIn(link.name, response.data['url'])
        self.assertEqual(datetime.strftime(link.expiring_time, "%H:%M:%S %d.%m.%y"), response.data['expiring_time'])
        os.remove('media/' + image.url.name)

    def test_generate_expiring_link_to_multiple_images(self):
        AccountTier.add_user_to_account_tier(self.account_tier_classes[2], self.user)
        image = Image.create_image(self.user, self.file)
        request = self.factory.post('link/', {'image_name': image.name, 'seconds': 300}, format='json')
        force_authenticate(request, self.user)
        request.user = self.user
        response = self.view(request)
        self.assertEqual(ExpiringLink.objects.count(), 1)
        self.assertEqual(ExpiringLink.objects.filter(image=image).count(), 1)
        link = ExpiringLink.objects.get(image=image)
        self.assertIn(link.name, response.data['url'])
        self.assertEqual(datetime.strftime(link.expiring_time, "%H:%M:%S %d.%m.%y"), response.data['expiring_time'])

        img = PILImage.new('RGB', (1000, 1000), color='red')
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='jpeg')
        file = SimpleUploadedFile('uploaded_file.jpg', img_bytes.getvalue(), content_type='image/jpeg')
        second_image = Image.create_image(self.user, file)
        request = self.factory.post('link/', {'image_name': second_image.name, 'seconds': 300}, format='json')
        force_authenticate(request, self.user)
        request.user = self.user
        response = self.view(request)
        self.assertEqual(ExpiringLink.objects.count(), 2)
        self.assertEqual(ExpiringLink.objects.filter(image=second_image).count(), 1)
        link = ExpiringLink.objects.get(image=second_image)
        self.assertIn(link.name, response.data['url'])
        self.assertEqual(datetime.strftime(link.expiring_time, "%H:%M:%S %d.%m.%y"), response.data['expiring_time'])
        os.remove('media/' + image.url.name)
        os.remove('media/' + second_image.url.name)

    def test_generate_expiring_link_with_changed_expires_link_to_false_after_image_creation(self):
        tier = AccountTier.add_user_to_account_tier(self.account_tier_classes[2], self.user)
        image = Image.create_image(self.user, self.file)
        tier.change_account_tier(self.account_tier_classes[1])
        request = self.factory.post('link/', {'image_name': image.name, 'seconds': 300}, format='json')
        force_authenticate(request, self.user)
        request.user = self.user
        response = self.view(request)
        self.assertEqual(ExpiringLink.objects.count(), 0)
        self.assertEqual(ExpiringLink.objects.filter(image=image).count(), 0)
        self.assertEqual(response.data['message'], 'Not allowed to generate expiring link')
        self.assertEqual(response.status_code, 403)
        os.remove('media/' + image.url.name)

    def test_generate_expiring_link_with_changed_original_image_to_false_after_image_creation(self):
        tier = AccountTier.add_user_to_account_tier(self.account_tier_classes[2], self.user)
        image = Image.create_image(self.user, self.file)
        tier.change_account_tier(self.account_tier_classes[0])
        request = self.factory.post('link/', {'image_name': image.name, 'seconds': 300}, format='json')
        force_authenticate(request, self.user)
        request.user = self.user
        response = self.view(request)
        self.assertEqual(ExpiringLink.objects.count(), 0)
        self.assertEqual(ExpiringLink.objects.filter(image=image).count(), 0)
        self.assertEqual(response.data['message'], 'Not allowed to generate expiring link')
        self.assertEqual(response.status_code, 403)
        os.remove('media/' + image.url.name)

    def test_generate_expiring_link_with_changed_expires_link_to_true_after_image_creation(self):
        tier = AccountTier.add_user_to_account_tier(self.account_tier_classes[1], self.user)
        image = Image.create_image(self.user, self.file)
        tier.change_account_tier(self.account_tier_classes[2])
        request = self.factory.post('link/', {'image_name': image.name, 'seconds': 300}, format='json')
        force_authenticate(request, self.user)
        request.user = self.user
        response = self.view(request)
        self.assertEqual(ExpiringLink.objects.count(), 1)
        self.assertEqual(ExpiringLink.objects.filter(image=image).count(), 1)
        link = ExpiringLink.objects.get(image=image)
        self.assertIn(link.name, response.data['url'])
        self.assertEqual(datetime.strftime(link.expiring_time, "%H:%M:%S %d.%m.%y"), response.data['expiring_time'])
        os.remove('media/' + image.url.name)

    def test_generate_expiring_link_with_changed_original_image_to_false_after_image_creation_with_original_image(self):
        tier = AccountTier.add_user_to_account_tier(self.account_tier_classes[1], self.user)
        image = Image.create_image(self.user, self.file)
        tier.change_account_tier(self.account_tier_classes[0])
        request = self.factory.post('link/', {'image_name': image.name, 'seconds': 300}, format='json')
        force_authenticate(request, self.user)
        request.user = self.user
        response = self.view(request)
        self.assertEqual(ExpiringLink.objects.count(), 0)
        self.assertEqual(ExpiringLink.objects.filter(image=image).count(), 0)
        self.assertEqual(response.data['message'], 'Not allowed to generate expiring link')
        self.assertEqual(response.status_code, 403)
        os.remove('media/' + image.url.name)

    def test_generate_expiring_link_with_original_image(self):
        AccountTier.add_user_to_account_tier(self.account_tier_classes[1], self.user)
        image = Image.create_image(self.user, self.file)
        request = self.factory.post('link/', {'image_name': image.name, 'seconds': 300}, format='json')
        force_authenticate(request, self.user)
        request.user = self.user
        response = self.view(request)
        self.assertEqual(ExpiringLink.objects.count(), 0)
        self.assertEqual(ExpiringLink.objects.filter(image=image).count(), 0)
        self.assertEqual(response.data['message'], 'Not allowed to generate expiring link')
        self.assertEqual(response.status_code, 403)
        os.remove('media/' + image.url.name)

    def test_generate_expiring_link_with_changed_link_to_true_after_image_creation_without_original_image(self):
        tier = AccountTier.add_user_to_account_tier(self.account_tier_classes[0], self.user)
        image = Image.create_image(self.user, self.file)
        tier.change_account_tier(self.account_tier_classes[2])
        request = self.factory.post('link/', {'image_name': image.name, 'seconds': 300}, format='json')
        force_authenticate(request, self.user)
        request.user = self.user
        response = self.view(request)
        self.assertEqual(ExpiringLink.objects.count(), 0)
        self.assertEqual(ExpiringLink.objects.filter(image=image).count(), 0)
        self.assertEqual(response.data['message'], 'Image not valid to generate expiring link')
        self.assertEqual(response.status_code, 409)

    def test_generate_expiring_link_with_changed_image_to_true_after_image_creation_without_original_image(self):
        tier = AccountTier.add_user_to_account_tier(self.account_tier_classes[0], self.user)
        image = Image.create_image(self.user, self.file)
        tier.change_account_tier(self.account_tier_classes[1])
        request = self.factory.post('link/', {'image_name': image.name, 'seconds': 300}, format='json')
        force_authenticate(request, self.user)
        request.user = self.user
        response = self.view(request)
        self.assertEqual(ExpiringLink.objects.count(), 0)
        self.assertEqual(ExpiringLink.objects.filter(image=image).count(), 0)
        self.assertEqual(response.data['message'], 'Not allowed to generate expiring link')
        self.assertEqual(response.status_code, 403)

    def test_generate_expiring_link_without_original_image(self):
        AccountTier.add_user_to_account_tier(self.account_tier_classes[0], self.user)
        image = Image.create_image(self.user, self.file)
        request = self.factory.post('link/', {'image_name': image.name, 'seconds': 300}, format='json')
        force_authenticate(request, self.user)
        request.user = self.user
        response = self.view(request)
        self.assertEqual(ExpiringLink.objects.count(), 0)
        self.assertEqual(ExpiringLink.objects.filter(image=image).count(), 0)
        self.assertEqual(response.data['message'], 'Not allowed to generate expiring link')
        self.assertEqual(response.status_code, 403)

    def test_generate_expiring_link_without_account_tier_original_image_and_expiring_link_on_image_creation(self):
        tier = AccountTier.add_user_to_account_tier(self.account_tier_classes[2], self.user)
        image = Image.create_image(self.user, self.file)
        tier.delete()
        request = self.factory.post('link/', {'image_name': image.name, 'seconds': 300}, format='json')
        force_authenticate(request, self.user)
        request.user = self.user
        response = self.view(request)
        self.assertEqual(ExpiringLink.objects.count(), 0)
        self.assertEqual(ExpiringLink.objects.filter(image=image).count(), 0)
        self.assertEqual(response.data['message'], 'Not allowed to generate expiring link')
        self.assertEqual(response.status_code, 403)
        os.remove('media/' + image.url.name)

    def test_generate_expiring_link_without_account_tier_original_image_on_image_creation(self):
        tier = AccountTier.add_user_to_account_tier(self.account_tier_classes[1], self.user)
        image = Image.create_image(self.user, self.file)
        tier.delete()
        request = self.factory.post('link/', {'image_name': image.name, 'seconds': 300}, format='json')
        force_authenticate(request, self.user)
        request.user = self.user
        response = self.view(request)
        self.assertEqual(ExpiringLink.objects.count(), 0)
        self.assertEqual(ExpiringLink.objects.filter(image=image).count(), 0)
        self.assertEqual(response.data['message'], 'Not allowed to generate expiring link')
        self.assertEqual(response.status_code, 403)
        os.remove('media/' + image.url.name)

    def test_generate_expiring_link_without_account_tier(self):
        tier = AccountTier.add_user_to_account_tier(self.account_tier_classes[0], self.user)
        image = Image.create_image(self.user, self.file)
        tier.delete()
        request = self.factory.post('link/', {'image_name': image.name, 'seconds': 300}, format='json')
        force_authenticate(request, self.user)
        request.user = self.user
        response = self.view(request)
        self.assertEqual(ExpiringLink.objects.count(), 0)
        self.assertEqual(ExpiringLink.objects.filter(image=image).count(), 0)
        self.assertEqual(response.data['message'], 'Not allowed to generate expiring link')
        self.assertEqual(response.status_code, 403)

    def test_generate_expiring_link_with_other_user_image(self):
        AccountTier.add_user_to_account_tier(self.account_tier_classes[2], self.user)
        image = Image.create_image(self.user, self.file)
        user = User(username='test1', password='test1')
        user.save()
        AccountTier.add_user_to_account_tier(self.account_tier_classes[2], user)
        request = self.factory.post('link/', {'image_name': image.name, 'seconds': 300}, format='json')
        force_authenticate(request, user)
        request.user = user
        response = self.view(request)
        self.assertEqual(ExpiringLink.objects.count(), 0)
        self.assertEqual(ExpiringLink.objects.filter(image=image).count(), 0)
        self.assertEqual(response.data['message'], 'Image does not exists')
        self.assertEqual(response.status_code, 404)
        os.remove('media/' + image.url.name)

    def test_generate_expiring_link_with_other_user_image_no_expiring_link_on_image_creation(self):
        AccountTier.add_user_to_account_tier(self.account_tier_classes[1], self.user)
        image = Image.create_image(self.user, self.file)
        user = User(username='test1', password='test1')
        user.save()
        AccountTier.add_user_to_account_tier(self.account_tier_classes[2], user)
        request = self.factory.post('link/', {'image_name': image.name, 'seconds': 300}, format='json')
        force_authenticate(request, user)
        request.user = user
        response = self.view(request)
        self.assertEqual(ExpiringLink.objects.count(), 0)
        self.assertEqual(ExpiringLink.objects.filter(image=image).count(), 0)
        self.assertEqual(response.data['message'], 'Image does not exists')
        self.assertEqual(response.status_code, 404)
        os.remove('media/' + image.url.name)

    def test_generate_expiring_link_with_other_user_image_no_original_image_on_image_creation(self):
        AccountTier.add_user_to_account_tier(self.account_tier_classes[0], self.user)
        image = Image.create_image(self.user, self.file)
        user = User(username='test1', password='test1')
        user.save()
        AccountTier.add_user_to_account_tier(self.account_tier_classes[2], user)
        request = self.factory.post('link/', {'image_name': image.name, 'seconds': 300}, format='json')
        force_authenticate(request, user)
        request.user = user
        response = self.view(request)
        self.assertEqual(ExpiringLink.objects.count(), 0)
        self.assertEqual(ExpiringLink.objects.filter(image=image).count(), 0)
        self.assertEqual(response.data['message'], 'Image does not exists')
        self.assertEqual(response.status_code, 404)

    def test_generate_expiring_link_with_other_user_image_and_no_expiring_link(self):
        AccountTier.add_user_to_account_tier(self.account_tier_classes[2], self.user)
        image = Image.create_image(self.user, self.file)
        user = User(username='test1', password='test1')
        user.save()
        AccountTier.add_user_to_account_tier(self.account_tier_classes[1], user)
        request = self.factory.post('link/', {'image_name': image.name, 'seconds': 300}, format='json')
        force_authenticate(request, user)
        request.user = user
        response = self.view(request)
        self.assertEqual(ExpiringLink.objects.count(), 0)
        self.assertEqual(ExpiringLink.objects.filter(image=image).count(), 0)
        self.assertEqual(response.data['message'], 'Not allowed to generate expiring link')
        self.assertEqual(response.status_code, 403)
        os.remove('media/' + image.url.name)

    def test_generate_expiring_link_with_other_user_image_and_no_expiring_link_and_no_expiring_link_on_creation(self):
        AccountTier.add_user_to_account_tier(self.account_tier_classes[1], self.user)
        image = Image.create_image(self.user, self.file)
        user = User(username='test1', password='test1')
        user.save()
        AccountTier.add_user_to_account_tier(self.account_tier_classes[1], user)
        request = self.factory.post('link/', {'image_name': image.name, 'seconds': 300}, format='json')
        force_authenticate(request, user)
        request.user = user
        response = self.view(request)
        self.assertEqual(ExpiringLink.objects.count(), 0)
        self.assertEqual(ExpiringLink.objects.filter(image=image).count(), 0)
        self.assertEqual(response.data['message'], 'Not allowed to generate expiring link')
        self.assertEqual(response.status_code, 403)
        os.remove('media/' + image.url.name)

    def test_generate_expiring_link_with_other_user_image_and_no_original_image_and_no_expiring_link_on_creation(self):
        AccountTier.add_user_to_account_tier(self.account_tier_classes[0], self.user)
        image = Image.create_image(self.user, self.file)
        user = User(username='test1', password='test1')
        user.save()
        AccountTier.add_user_to_account_tier(self.account_tier_classes[1], user)
        request = self.factory.post('link/', {'image_name': image.name, 'seconds': 300}, format='json')
        force_authenticate(request, user)
        request.user = user
        response = self.view(request)
        self.assertEqual(ExpiringLink.objects.count(), 0)
        self.assertEqual(ExpiringLink.objects.filter(image=image).count(), 0)
        self.assertEqual(response.data['message'], 'Not allowed to generate expiring link')
        self.assertEqual(response.status_code, 403)

    def test_generate_expiring_link_with_other_user_image_and_no_original_image_and_expiring_link(self):
        AccountTier.add_user_to_account_tier(self.account_tier_classes[2], self.user)
        image = Image.create_image(self.user, self.file)
        user = User(username='test1', password='test1')
        user.save()
        AccountTier.add_user_to_account_tier(self.account_tier_classes[0], user)
        request = self.factory.post('link/', {'image_name': image.name, 'seconds': 300}, format='json')
        force_authenticate(request, user)
        request.user = user
        response = self.view(request)
        self.assertEqual(ExpiringLink.objects.count(), 0)
        self.assertEqual(ExpiringLink.objects.filter(image=image).count(), 0)
        self.assertEqual(response.data['message'], 'Not allowed to generate expiring link')
        self.assertEqual(response.status_code, 403)
        os.remove('media/' + image.url.name)

    def test_generate_expiring_link_with_other_user_image_and_no_original_image_and_expiring_link_no_link_on_creation(self):
        AccountTier.add_user_to_account_tier(self.account_tier_classes[1], self.user)
        image = Image.create_image(self.user, self.file)
        user = User(username='test1', password='test1')
        user.save()
        AccountTier.add_user_to_account_tier(self.account_tier_classes[0], user)
        request = self.factory.post('link/', {'image_name': image.name, 'seconds': 300}, format='json')
        force_authenticate(request, user)
        request.user = user
        response = self.view(request)
        self.assertEqual(ExpiringLink.objects.count(), 0)
        self.assertEqual(ExpiringLink.objects.filter(image=image).count(), 0)
        self.assertEqual(response.data['message'], 'Not allowed to generate expiring link')
        self.assertEqual(response.status_code, 403)
        os.remove('media/' + image.url.name)

    def test_generate_expiring_link_with_other_user_image_and_no_original_image_and_expiring_link_no_image_on_creation(self):
        AccountTier.add_user_to_account_tier(self.account_tier_classes[0], self.user)
        image = Image.create_image(self.user, self.file)
        user = User(username='test1', password='test1')
        user.save()
        AccountTier.add_user_to_account_tier(self.account_tier_classes[0], user)
        request = self.factory.post('link/', {'image_name': image.name, 'seconds': 300}, format='json')
        force_authenticate(request, user)
        request.user = user
        response = self.view(request)
        self.assertEqual(ExpiringLink.objects.count(), 0)
        self.assertEqual(ExpiringLink.objects.filter(image=image).count(), 0)
        self.assertEqual(response.data['message'], 'Not allowed to generate expiring link')
        self.assertEqual(response.status_code, 403)

    def test_generate_expiring_link_to_other_user_image_without_account_tier(self):
        AccountTier.add_user_to_account_tier(self.account_tier_classes[2], self.user)
        image = Image.create_image(self.user, self.file)
        user = User(username='test1', password='test1')
        user.save()
        request = self.factory.post('link/', {'image_name': image.name, 'seconds': 300}, format='json')
        force_authenticate(request, user)
        request.user = user
        response = self.view(request)
        self.assertEqual(ExpiringLink.objects.count(), 0)
        self.assertEqual(ExpiringLink.objects.filter(image=image).count(), 0)
        self.assertEqual(response.data['message'], 'Not allowed to generate expiring link')
        self.assertEqual(response.status_code, 403)
        os.remove('media/' + image.url.name)

    def test_generate_expiring_link_without_authentication(self):
        AccountTier.add_user_to_account_tier(self.account_tier_classes[2], self.user)
        image = Image.create_image(self.user, self.file)
        request = self.factory.post('link/', {'image_name': image.name, 'seconds': 300}, format='json')
        request.user = AnonymousUser()
        response = self.view(request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(ExpiringLink.objects.count(), 0)
        self.assertEqual(ExpiringLink.objects.filter(image=image).count(), 0)
        os.remove('media/' + image.url.name)
