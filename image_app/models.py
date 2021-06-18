from django.db import models
from django.core.validators import MinValueValidator
from django.contrib.auth.models import User


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


class AccountTier(models.Model):
    tier = models.ForeignKey(AccountTierClass, on_delete=models.CASCADE)
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.tier) + ': ' + self.user.username


class Image(models.Model):
    name = models.CharField(max_length=50, unique=True)
    url = models.URLField(max_length=200, unique=True, null=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Thumbnail(models.Model):
    name = models.CharField(max_length=60, unique=True)
    url = models.URLField(max_length=210, unique=True)
    image = models.ForeignKey(Image, on_delete=models.CASCADE)
    thumbnail_size = models.ForeignKey(ThumbnailSize, on_delete=models.CASCADE)

    def __str__(self):
        return self.name
