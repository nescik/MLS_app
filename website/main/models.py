import re
from typing import Any
from django.db import models
from django.contrib.auth.models import User, Group
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
        return f'{self.user.get_full_name()}'
    
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
    members = models.ManyToManyField(User, through='TeamMembership', related_name='team_member', blank=True)
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
    
    def get_members(self):
        return TeamMembership.objects.filter(team=self)

    class Meta:
        permissions = [
            ("add_new_member", "Can add new team memeber"),
            ("delete_member", "Can delete team memeber"),
            ("manage_perms", "Can manage all permission in team"),
            ("view_logs", "Can see team logs")
        ]   



class TeamMembership(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    groups = models.ManyToManyField(Group)

    def __str__(self):
        return f'{self.team}--{self.user.get_full_name()}'
    
    def get_fullname_member(self):
        return f'{self.user.get_full_name()}'

class TeamMessage(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    upload_date = models.DateTimeField(default=timezone.now)
    content = models.TextField(max_length=500, blank=True, null=True)

class TeamActivityLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    action = models.CharField(max_length=150)
    timestamp = models.DateTimeField(default=timezone.now)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)


class CustomFileExtensionValidator(FileExtensionValidator):
    message = 'Niedozwolone rozszerzenie pliku. Akceptowane rozszerzenia to: %(allowed_extensions)s'


def upload_to_team_folder(instance, filename):
    team_name = instance.team.name
    base_name, ext = os.path.splitext(filename)

    # Sprawdź, czy plik ma już suffix v_
    existing_suffix = re.search(r'_v(\d+)', base_name)
    
    # Jeżeli plik ma już suffix v_, to zaktualizuj go, w przeciwnym razie dodaj nowy suffix
    if existing_suffix:
        current_version = int(existing_suffix.group(1))
        new_version = instance.version
        if new_version > current_version:
            base_name = re.sub(r'_v(\d+)', f'_v{new_version}', base_name)
    else:
        version_suffix = f"_v{instance.version}" if instance.version > 1 else ""
        base_name = f'{base_name}{version_suffix}'

    return f'team_files/team_{team_name}/{base_name}{ext}'


gd_storage = GoogleDriveStorage()

class File(models.Model):

    PRIVACY_CHOICES = [
        ('public', 'Publiczny'),
        ('confidencial', 'Poufny'),
        ('secret', 'Tajny')
    ]

    class Meta:
        permissions = [
            ('download_file', 'Can download file'),
            ('view_confidencial', 'Can view confidencial files'),
            ('edit_confidencial', 'Can edit confidencial files'),
            ('download_confidencial', 'Can download confidencial files'),
            ('view_secret', 'Can view secret files'),
            ('edit_secret', 'Can edit secret files'),
            ('download_secret', 'Can download secret files'),
        ]   


    description = models.CharField(max_length=255)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    file = models.FileField(upload_to=upload_to_team_folder, storage=gd_storage, validators=[CustomFileExtensionValidator(['pdf', 'doc', 'docx'])])
    upload_date = models.DateTimeField(default=timezone.now)
    version = models.SmallIntegerField(default=1)
    last_editor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='last_edited_files')
    privacy_level = models.CharField(max_length=12, choices=PRIVACY_CHOICES, default='public')

    def __str__(self):
        return self.file.name
    
    def get_file_name(self):
        return os.path.basename(self.file.name)
    

    def get_team_key(self):
        master_key = settings.ENCRYPT_KEY
        fernet = Fernet(master_key)

        encrypted_team_key = self.team.key.value.encode()
        decrypted_team_key = fernet.decrypt(encrypted_team_key)
        fernet_team = Fernet(decrypted_team_key)

        return fernet_team
    


    def download(self, request):

        if self.team.key:
            
            fernet_team = self.get_team_key()
            
            encrypt_content = self.file.read()
            decrypted_content = fernet_team.decrypt(encrypt_content)
            mime_type, _ = guess_type(self.file.name)
            response = HttpResponse(decrypted_content, content_type=mime_type)
            response['Content-Disposition'] = f'attachment; filename="{os.path.basename(self.file.name)}"'

        return response

    def save(self, *args, **kwargs):

        if self.team.key:
            fernet_team = self.get_team_key()

            file_content = self.file.read()
            encrypted_content = fernet_team.encrypt(file_content)
            self.file.save(self.file.name, ContentFile(encrypted_content), save=False)

        super().save(*args, **kwargs)