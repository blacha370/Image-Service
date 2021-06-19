from . import models
from PIL import Image
from math import ceil
import io


def resize_thumbnail(file, height):
    image = Image.open(file)
    ratio = image.height / height
    image = image.resize((ceil(image.width / ratio), height))
    return image


def save_photo(file, photo):
    if not isinstance(photo, (models.Thumbnail, models.Image)):
        raise TypeError
    elif isinstance(photo, models.Thumbnail):
        image = resize_thumbnail(file, photo.thumbnail_size.height)
        image.save(photo.url[1:])
    else:
        image = Image.open(file)
        image.save(photo.url[1:])
        return file
    img_bytes = io.BytesIO()
    if photo.name[-3:] == 'jpg':
        image.save(img_bytes, format='jpeg')
    else:
        image.save(img_bytes, format='png')
    return img_bytes
