from django.db import models

from django.contrib.auth.models import User
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver

@receiver(pre_save, sender = User)
def update_username_from_email(sender, instance, **kwargs):
    instance.username = instance.email

@receiver(post_save, sender = User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user = instance)

@receiver(post_save, sender = User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

class Profile (models.Model):
    user = models.OneToOneField(User, on_delete = models.CASCADE)
    nickname = models.CharField(max_length = 255)