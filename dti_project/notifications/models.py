from django.db import models
from users.models import User

# Create your models here.

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    url = models.URLField(blank=True, null=True) # optional: link to a page
    is_read = models.BooleanField(default=False)
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        status = "Unread" if not self.is_read else "Read"
        return f"{status} Notification for {self.user.username}: {self.message[:20]}"