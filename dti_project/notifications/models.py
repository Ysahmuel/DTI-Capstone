from django.db import models
from users.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
# Create your models here.

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    sender = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='sent_notifications')
    message = models.TextField()
    url = models.URLField(blank=True, null=True) # optional: link to a page
    is_read = models.BooleanField(default=False)
    date = models.DateField(auto_now_add=True)

    # Generic relation fields
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    document = GenericForeignKey("content_type", "object_id")

    NOTIFICATION_TYPES = [
        ("update_request", "Update Request"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
        ("info", "Info"),
    ]
    type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES, default="info")

    def __str__(self):
        status = "Unread" if not self.is_read else "Read"
        return f"{status} Notification for {self.user.username}: {self.message[:20]}"
    
    def display_message(self):
        return