from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission

# Create your models here.
class User(AbstractUser):
    class Roles(models.TextChoices):
        BUSINESS_OWNER = "business_owner", "Business Owner"
        ADMIN = "admin", "Admin"

    profile_picture = models.ImageField(
        upload_to='profile_pictures/',
        default='profile_pictures/default-avatar-icon.jpg',
        blank=True
    )
    role = models.CharField(
        max_length=20,
        choices=Roles.choices,
        default=Roles.BUSINESS_OWNER
    )

    def __str__(self):
        return f"{self.first_name} {self.last_name}"