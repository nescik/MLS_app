from typing import Any
from django.db import models
from django.contrib.auth.models import User
from django.utils.deconstruct import deconstructible
import os
import uuid
from PIL import Image, ExifTags
from django_countries.fields import CountryField
from django.utils import timezone
from django.core.validators import FileExtensionValidator
from django.http import HttpResponse
from mimetypes import guess_type
from gdstorage.storage import GoogleDriveStorage
from cryptography.fernet import Fernet
from django.conf import settings
from django.core.files.base import ContentFile

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
    bio = models.TextField(max_length=500, blank=True, null=True)
    country = CountryField(default = 'PL')
    age = models.PositiveSmallIntegerField(blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    website = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self) :
        return f'{self.user.username} Profile'
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        img = Image.open(self.image.path)

        try:
            for orientation in ExifTags.TAGS.keys():
                if ExifTags.TAGS[orientation] == 'Orientation':
                    break
            exif = dict(img._getexif().items())
            if exif[orientation] == 3:
                img = img.rotate(180, expand=True)
            elif exif[orientation] == 6:
                img = img.rotate(270, expand=True)
            elif exif[orientation] == 8:
                img = img.rotate(90, expand=True)
        except (AttributeError, KeyError, IndexError):
            pass

        if img.height > 300 or img.width > 300:
            output_size = (300, 300)
            img.thumbnail(output_size)
            img.save(self.image.path)

    def is_profile_complete(self):
        return bool(self.user.first_name and self.user.last_name)

class Key(models.Model):
    value = models.CharField(max_length=44)
        
class Team(models.Model):
    name = models.CharField(max_length=255)
    founder = models.ForeignKey(User, on_delete=models.CASCADE, related_name='team_founder')
    members = models.ManyToManyField(User, related_name='team_member', blank=True)
    key = models.OneToOneField(Key, on_delete=models.SET_NULL, null=True, blank=True, related_name='team_key', unique=True)

    def save(self, *args, **kwargs):
        if not self.key_id:
            new_key = Fernet.generate_key()

            master_key = settings.ENCRYPT_KEY
            fernet = Fernet(master_key)
            encrypted_key = fernet.encrypt(new_key)

            key_instance = Key(value=encrypted_key.decode())
            key_instance.save()
            self.key = key_instance

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
    

class CustomFileExtensionValidator(FileExtensionValidator):
    message = 'Niedozwolone rozszerzenie pliku. Akceptowane rozszerzenia to: %(allowed_extensions)s'


def upload_to_team_folder(instance, filename):
    return f'team_files/team_{instance.team.name}/{filename}'


gd_storage = GoogleDriveStorage()
cipher_suite = Fernet(key=settings.ENCRYPT_KEY)

def encrypt_file(file_content):
    return cipher_suite.encrypt(file_content)

def decrypt_file(encrypt_content):
    return cipher_suite.decrypt(encrypt_content)



class File(models.Model):
    description = models.CharField(max_length=255)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    file = models.FileField(upload_to=upload_to_team_folder, storage=gd_storage, validators=[CustomFileExtensionValidator(['pdf', 'doc', 'docx'])])
    upload_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.file.name
    
    def get_file_name(self):
        return os.path.basename(self.file.name)
    

    def _get_team_key(self):
        master_key = settings.ENCRYPT_KEY
        fernet = Fernet(master_key)

        encrypted_team_key = self.team.key.value.encode()
        decrypted_team_key = fernet.decrypt(encrypted_team_key)
        fernet_team = Fernet(decrypted_team_key)

        return fernet_team


    def download(self, request):

        if self.team.key:
            
            fernet_team = self._get_team_key()
            
            encrypt_content = self.file.read()
            decrypted_content = fernet_team.decrypt(encrypt_content)
            mime_type, _ = guess_type(self.file.name)
            response = HttpResponse(decrypted_content, content_type=mime_type)
            response['Content-Disposition'] = f'attachment; filename="{os.path.basename(self.file.name)}"'

        return response

    def save(self, *args, **kwargs):

        if self.team.key:
            fernet_team = self._get_team_key()

            file_content = self.file.read()
            encrypted_content = fernet_team.encrypt(file_content)
            self.file.save(self.file.name, ContentFile(encrypted_content), save=False)

        super().save(*args, **kwargs)