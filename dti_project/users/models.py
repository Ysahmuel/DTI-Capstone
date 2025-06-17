from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission

# Create your models here.
class User(AbstractUser):
    groups = models.ManyToManyField(
        Group,
        related_name='custom_user_set',
        blank=True,
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='custom_user_set',
        blank=True,
    )