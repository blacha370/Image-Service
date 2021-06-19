from django.db import models
from django.core.validators import MinValueValidator
from django.contrib.auth.models import User
from datetime import datetime
from image_service.settings import STATIC_URL


class ThumbnailSize(models.Model):
    height = models.IntegerField(unique=True, validators=[MinValueValidator(1)])

    def __str__(self):
        return str(self.height)

    @classmethod
    def get_or_create_validated(cls, height):
        if not isinstance(height, int) or isinstance(height, bool):
            raise TypeError
        elif height <= 0:
            raise ValueError
        return cls.objects.get_or_create(height=height)[0]


class AccountTierClass(models.Model):
    name = models.CharField(max_length=50, unique=True)
    original_image = models.BooleanField(default=False)
    expires_link = models.BooleanField(default=False)
    thumbnail_sizes = models.ManyToManyField(ThumbnailSize)

    def __str__(self):
        return self.name

    @classmethod
    def get_or_create_validated(cls, name, thumbnail_sizes, original_image=False, expires_link=False):
        if not isinstance(name, str) or [size for size in thumbnail_sizes if not isinstance(size, ThumbnailSize)] \
                or not len(thumbnail_sizes )or not isinstance(original_image, bool) or not \
                isinstance(expires_link, bool):
            raise TypeError
        elif len(name) > 50 or cls.objects.filter(name=name) or\
                cls._check_if_same_tier_class_exists(thumbnail_sizes, original_image, expires_link):
            raise ValueError
        account_tier_class = cls(name=name, original_image=original_image, expires_link=expires_link)
        account_tier_class.save()
        account_tier_class.thumbnail_sizes.add(*thumbnail_sizes)
        return account_tier_class

    @classmethod
    def _check_if_same_tier_class_exists(cls, thumbnail_sizes, original_image, expires_link):
        tiers = cls.objects.filter(thumbnail_sizes__in=[size.id for size in thumbnail_sizes],
                                   original_image=original_image, expires_link=expires_link)
        for tier in tiers:
            if thumbnail_sizes == list(tier.thumbnail_sizes.all()):
                return True
        return False


class AccountTier(models.Model):
    tier = models.ForeignKey(AccountTierClass, on_delete=models.CASCADE)
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.tier) + ': ' + self.user.username

    @classmethod
    def add_user_to_account_tier(cls, tier, user):
        if not isinstance(tier, AccountTierClass) or not isinstance(user, User):
            raise TypeError
        elif cls.objects.filter(user=user).count():
            raise ValueError
        account_tier = cls(tier=tier, user=user)
        account_tier.save()
        return account_tier

    def change_account_tier(self, tier):
        if not isinstance(tier, AccountTierClass):
            raise TypeError
        elif self.tier == tier:
            raise ValueError
        self.tier = tier
        self.save()
        return self


class Image(models.Model):
    name = models.CharField(max_length=50, unique=True)
    url = models.URLField(max_length=200, unique=True, null=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    @classmethod
    def _generate_name(cls, extension, owner):
        name = str(owner.pk) + str(int(datetime.now().timestamp())) + str(cls.objects.filter(owner=owner).count())
        return name + extension

    @staticmethod
    def _generate_url(name, owner):
        if AccountTier.objects.get(user=owner).tier.original_image:
            return STATIC_URL + name
        return

    @classmethod
    def create_image(cls, owner, extension):
        if not isinstance(owner, User) or not isinstance(extension, str):
            raise TypeError
        if extension not in ['.jpg', '.png']:
            raise ValueError
        name = cls._generate_name(extension, owner)
        url = cls._generate_url(name, owner)
        image = cls(name=name, url=url, owner=owner)
        image.save()
        return image


class Thumbnail(models.Model):
    name = models.CharField(max_length=60, unique=True)
    url = models.URLField(max_length=210, unique=True)
    image = models.ForeignKey(Image, on_delete=models.CASCADE)
    thumbnail_size = models.ForeignKey(ThumbnailSize, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    @classmethod
    def _generate_name(cls, image, thumbnail_size):
        index = image.name.rfind('.')
        image_name, extension = image.name[:index], image.name[index:]
        name = image_name + '_' + str(thumbnail_size.height) + extension
        if cls.objects.filter(name=name).count():
            raise ValueError
        return name

    @staticmethod
    def _generate_url(name):
        return STATIC_URL + name

    @classmethod
    def create_thumbnail(cls, image, thumbnail_size):
        if not isinstance(image, Image) or not isinstance(thumbnail_size, ThumbnailSize):
            raise TypeError
        if thumbnail_size not in AccountTier.objects.get(user=image.owner).tier.thumbnail_sizes.all():
            raise ValueError
        name = cls._generate_name(image, thumbnail_size)
        url = cls._generate_url(name)
        thumbnail = cls(name=name, url=url, image=image, thumbnail_size=thumbnail_size)
        thumbnail.save()
        return thumbnail

    @property
    def size(self):
        return str(self.thumbnail_size.height) + 'px'
