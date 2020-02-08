from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.db.models.signals import post_save
from django.dispatch import receiver

from .validators import UsernameValidator

class User(AbstractUser):
    username_validator = UsernameValidator()

    username = models.CharField(
        _('username'),
        max_length=30,
        unique=True,
        help_text=_(
            """
                Required. 30 characters or fewer. Letters, numbers,
                underscores, and hyphens only.
            """
        ),
        validators=[username_validator],
        error_messages={
            'unique': _("A user with that username already exists."),
        },
    )

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    instance.profile.save()
