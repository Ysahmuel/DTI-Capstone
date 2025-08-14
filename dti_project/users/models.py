from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission

# Create your models here.
class User(AbstractUser):
    profile_picture = models.ImageField(
        upload_to='profile_pictures/',
        default='profile_pictures/default-avatar-icon.jpg',
        blank=True
    )

    def __str__(self):
        return f"{self.first_name} {self.last_name}"