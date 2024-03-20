from django.db.models.signals import post_save, pre_delete
from django.contrib.auth.models import User
from .models import Profile
from django.dispatch import receiver
from axes.signals import user_locked_out


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance) 

@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    instance.profile.save()


@receiver(user_locked_out)
def handle_user_locked_out(sender, request, username, **kwargs):
    user = User.objects.get(username=username)
    user.is_active = False
    user.save()
