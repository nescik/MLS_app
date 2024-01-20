from django.db import models
from django.contrib.auth.models import User
from django.utils.deconstruct import deconstructible
import os
import uuid

@deconstructible
class UniqueFileName:
    def __init__(self, path):
        self.path = path

    def __call__(self, instance, filename):
        ext = filename.split('.')[-1]
        filename = f"{uuid.uuid4().hex}.{ext}"
        return os.path.join(self.path, filename)

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(default='default.jpg', upload_to=UniqueFileName('profile_pics'))

    def __str__(self) :
        return f'{self.user.username} Profile'
        