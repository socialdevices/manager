from core import models
from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save

#Create your models here.


class UserProfile(models.Model):
    # This field is required.
    user = models.OneToOneField(User, unique=True)

    # Others
    nickname = models.CharField(max_length=20)


def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

post_save.connect(create_user_profile, sender=User)
