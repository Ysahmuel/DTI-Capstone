from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from users.models import User

class ChangeRequest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='requests')
    date = models.DateTimeField(auto_now_add=True)

    # Generic link to any document/form
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    document = GenericForeignKey('content_type', 'object_id')

    # Proposed changes stored as JSON
    proposed_changes = models.JSONField(
        default=dict,
        blank=True,
        help_text="Proposed field changes (field_name -> new_value)"
    )

    # Approval by the document owner
    is_approved = models.BooleanField(default=False)
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, related_name='approved_requests')  # owner

    class Meta:
        unique_together = ("content_type", "object_id")  # one request per document

    def __str__(self):
        return f"Update request for {self.document} by {self.user}"