from django.core.files import File
from PIL import Image
from math import ceil
import io
from . import models


def resize_thumbnail(file, height):
    image = Image.open(file)
    ratio = image.height / height
    image = image.resize((ceil(image.width / ratio), height))
    return image


def save_photo(file, photo):
    if not isinstance(photo, models.Thumbnail):
        raise TypeError
    img_bytes = io.BytesIO()
    image = resize_thumbnail(file, photo.thumbnail_size.height)
    if photo.name[-3:] == 'jpg':
        image.save(img_bytes, format='jpeg')
    else:
        image.save(img_bytes, format='png')
    file = File(img_bytes, name=photo.name)
    return file
