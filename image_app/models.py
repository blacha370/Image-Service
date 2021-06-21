from django.db import models
from django.core.validators import MinValueValidator
from django.contrib.auth.models import User
from datetime import datetime, timedelta
from .functions import save_photo
from django.core.files import File


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
    expiring_link = models.BooleanField(default=False)
    thumbnail_sizes = models.ManyToManyField(ThumbnailSize)

    def __str__(self):
        return self.name

    @classmethod
    def get_or_create_validated(cls, name, thumbnail_sizes, original_image=False, expiring_link=False):
        if not isinstance(name, str) or [size for size in thumbnail_sizes if not isinstance(size, ThumbnailSize)] \
                or not len(thumbnail_sizes) or not isinstance(original_image, bool) or not \
                isinstance(expiring_link, bool):
            raise TypeError
        if not original_image:
            expiring_link = False
        if len(name) > 50 or cls.objects.filter(name=name) or\
                cls._check_if_same_tier_class_exists(thumbnail_sizes, original_image, expiring_link):
            raise ValueError
        account_tier_class = cls(name=name, original_image=original_image, expiring_link=expiring_link)
        account_tier_class.save()
        account_tier_class.thumbnail_sizes.add(*thumbnail_sizes)
        return account_tier_class

    @classmethod
    def _check_if_same_tier_class_exists(cls, thumbnail_sizes, original_image, expiring_link):
        tiers = cls.objects.filter(thumbnail_sizes__in=[size.id for size in thumbnail_sizes],
                                   original_image=original_image, expiring_link=expiring_link)
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
    url = models.ImageField(upload_to='images/', blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    @classmethod
    def _generate_name(cls, extension, owner):
        if extension not in ['.jpg', '.png']:
            raise ValueError
        name = str(owner.pk) + str(int(datetime.now().timestamp())) + str(cls.objects.filter(owner=owner).count())
        return name + extension

    @classmethod
    def create_image(cls, owner, file):
        if not isinstance(owner, User) or not isinstance(file, File):
            raise TypeError
        account_tier = AccountTier.objects.get(user=owner).tier
        name = cls._generate_name(file.name[-4:], owner)
        image = cls(name=name, owner=owner)
        image.save()
        if account_tier.original_image:
            image._upload_image(file)
        return image

    def _upload_image(self, file):
        file.name = self.name
        self.url = file
        self.save()


class Thumbnail(models.Model):
    name = models.CharField(max_length=60, unique=True)
    url = models.ImageField(upload_to='thumbnails/', null=True)
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

    @classmethod
    def create_thumbnail(cls, image, thumbnail_size, file):
        if not isinstance(image, Image) or not isinstance(thumbnail_size, ThumbnailSize) or not isinstance(file, File):
            raise TypeError
        if thumbnail_size not in AccountTier.objects.get(user=image.owner).tier.thumbnail_sizes.all() or \
                Thumbnail.objects.filter(image=image, thumbnail_size=thumbnail_size).count():
            raise ValueError
        name = cls._generate_name(image, thumbnail_size)
        thumbnail = cls(name=name, image=image, thumbnail_size=thumbnail_size)
        thumbnail.save()
        file = save_photo(file, thumbnail)
        thumbnail._upload_thumbnail(file)
        return file, thumbnail

    def _upload_thumbnail(self, file):
        file.name = self.name
        self.url = file
        self.save()

    @property
    def size(self):
        return str(self.thumbnail_size.height) + 'px'


class ExpiringLink(models.Model):
    image = models.ForeignKey(Image, on_delete=models.CASCADE)
    name = models.CharField(max_length=50, unique=True)
    expiring_time = models.DateTimeField()

    @classmethod
    def generate(cls, image, seconds):
        if not isinstance(image, Image) or not isinstance(seconds, int) or isinstance(seconds, bool):
            raise TypeError
        if not 300 <= seconds <= 30000 or image.url.name == '':
            raise ValueError
        now = datetime.now()
        name = str(cls.objects.count()) + str(int(now.timestamp())) + image.name
        expiring_time = now + timedelta(seconds=seconds)
        link = cls(image=image, name=name, expiring_time=expiring_time)
        link.save()
        return link
