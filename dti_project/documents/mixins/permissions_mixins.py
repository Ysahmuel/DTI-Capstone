from django.contrib import messages
from django.shortcuts import redirect

class OwnershipDraftMixin:
    """
    Ensures that only the owning user can edit an object,
    and only if the object is still in draft status.
    """

    draft_only = True  # set to False if some forms can bypass draft restriction

    def post(self, request, *args, **kwargs):
        obj = self.get_object()

        # Ownership check
        if hasattr(obj, "user") and obj.user != request.user:
            messages.error(request, "You cannot edit this item.")
            return redirect("/")

        # Status check (optional toggle)
        if self.draft_only and hasattr(obj, "status") and obj.status != "draft":
            messages.error(request, "You can only edit drafts.")
            return redirect("/")

        return super().post(request, *args, **kwargs)