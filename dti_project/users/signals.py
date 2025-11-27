from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import ActivityLog
from .utils import log_activity
from documents.models import (
    SalesPromotionPermitApplication,
    ServiceRepairAccreditationApplication,
    OrderOfPayment,
)

User = get_user_model()

def _get_user_from_instance(instance):
    """Try common fields that point to the acting user; views can set _request_user before saving."""
    user = getattr(instance, "_request_user", None)
    if user:
        return user
    for attr in ("approved_by","verified_by","submitted_by","created_by","modified_by","updated_by","owner","user"):
        u = getattr(instance, attr, None)
        if u:
            return u
    for attr in ("approved_by_id","verified_by_id","submitted_by_id","created_by_id","user_id"):
        uid = getattr(instance, attr, None)
        if uid:
            try:
                return User.objects.get(pk=uid)
            except Exception:
                pass
    return None

def _get_object_display_name(obj):
    model_name = obj.__class__.__name__
    obj_id = getattr(obj, "id", getattr(obj, "pk", None)) or "?"
    name_map = {
        "SalesPromotionPermitApplication": "Promo",
        "ServiceRepairAccreditationApplication": "SRA",
        "OrderOfPayment": "Payment",
    }
    label = name_map.get(model_name, model_name)
    return f"{label} #{obj_id}"

# PRE-SAVE: capture previous status/payment fields for change detection
@receiver(pre_save, sender=ServiceRepairAccreditationApplication)
def sra_capture_prev(sender, instance, **kwargs):
    if not instance.pk:
        instance._previous_status = None
        return
    try:
        prev = sender.objects.get(pk=instance.pk)
        instance._previous_status = getattr(prev, "status", None)
    except sender.DoesNotExist:
        instance._previous_status = None

@receiver(pre_save, sender=SalesPromotionPermitApplication)
def sppa_capture_prev(sender, instance, **kwargs):
    if not instance.pk:
        instance._previous_status = None
        return
    try:
        prev = sender.objects.get(pk=instance.pk)
        instance._previous_status = getattr(prev, "status", None)
    except sender.DoesNotExist:
        instance._previous_status = None

@receiver(pre_save, sender=OrderOfPayment)
def oop_capture_prev(sender, instance, **kwargs):
    if not instance.pk:
        instance._previous_payment_status = None
        return
    try:
        prev = sender.objects.get(pk=instance.pk)
        instance._previous_payment_status = getattr(prev, "payment_status", getattr(prev, "status", None))
    except sender.DoesNotExist:
        instance._previous_payment_status = None

# SRA: submissions and approvals
@receiver(post_save, sender=ServiceRepairAccreditationApplication)
def sra_saved(sender, instance, created, **kwargs):
    actor = _get_user_from_instance(instance)
    obj_label = _get_object_display_name(instance)

    if created:
        # Business owner submission -> "Submitted new SRA"
        action = f"Submitted new SRA"
        action_type = ActivityLog.ActionType.SUBMITTED
    else:
        prev = getattr(instance, "_previous_status", None)
        curr = getattr(instance, "status", None)
        if prev and curr and prev != curr:
            if str(curr).lower() == "approved":
                action = f"Approved {obj_label}"
                action_type = ActivityLog.ActionType.APPROVED
            else:
                action = f"Updated status of {obj_label} from {prev} → {curr}"
                action_type = ActivityLog.ActionType.STATUS_CHANGE
        else:
            action = f"Updated {obj_label}"
            action_type = ActivityLog.ActionType.UPDATE

    log_activity(
        user=actor,
        action=action,
        action_type=action_type,
        obj=instance,
        visibility="public"
    )

# Sales Promotion: creations/updates (map create to "Submitted" if needed)
@receiver(post_save, sender=SalesPromotionPermitApplication)
def sppa_saved(sender, instance, created, **kwargs):
    actor = _get_user_from_instance(instance)
    obj_label = _get_object_display_name(instance)

    if created:
        action = f"Submitted new Promo"
        action_type = ActivityLog.ActionType.SUBMITTED
    else:
        prev = getattr(instance, "_previous_status", None)
        curr = getattr(instance, "status", None)
        if prev and curr and prev != curr:
            if str(curr).lower() == "approved":
                action = f"Approved {obj_label}"
                action_type = ActivityLog.ActionType.APPROVED
            else:
                action = f"Updated status of {obj_label} from {prev} → {curr}"
                action_type = ActivityLog.ActionType.STATUS_CHANGE
        else:
            action = f"Updated {obj_label}"
            action_type = ActivityLog.ActionType.UPDATE

    log_activity(
        user=actor,
        action=action,
        action_type=action_type,
        obj=instance,
        visibility="public"
    )

# OrderOfPayment: payment events -> produce "Verified payment for Promo #55" when appropriate
@receiver(post_save, sender=OrderOfPayment)
def order_of_payment_saved(sender, instance, created, **kwargs):
    actor = _get_user_from_instance(instance)
    prev = getattr(instance, "_previous_payment_status", None)
    curr = getattr(instance, "payment_status", getattr(instance, "status", None))
    # try to get related document label if available
    related_obj = getattr(instance, "document", None) or getattr(instance, "related_object", None)
    if related_obj:
        obj_label = _get_object_display_name(related_obj)
    else:
        obj_label = _get_object_display_name(instance)

    if created:
        action = f"Initiated payment for {obj_label}"
        action_type = ActivityLog.ActionType.PAYMENT_INITIATED
    else:
        if prev and curr and prev != curr:
            lower = str(curr).lower()
            if lower in ("verified", "paid"):
                # Use "Verified payment for Promo #55" phrasing
                # If related_obj is a Promo/SRA, adapt label wording
                if related_obj and related_obj.__class__.__name__ == "SalesPromotionPermitApplication":
                    action = f"Verified payment for Promo #{getattr(related_obj,'id',getattr(related_obj,'pk','?'))}"
                else:
                    action = f"Verified payment for {obj_label}"
                action_type = ActivityLog.ActionType.PAYMENT_VERIFIED
            elif lower in ("failed", "error"):
                action = f"Payment failed for {obj_label}"
                action_type = ActivityLog.ActionType.PAYMENT_FAILED
            else:
                action = f"Updated payment status for {obj_label} from {prev} → {curr}"
                action_type = ActivityLog.ActionType.STATUS_CHANGE
        else:
            action = f"Updated Order of Payment {obj_label}"
            action_type = ActivityLog.ActionType.UPDATE

    log_activity(
        user=actor,
        action=action,
        action_type=action_type,
        obj=instance,
        visibility="public"
    )

# Deletions
@receiver(post_delete, sender=ServiceRepairAccreditationApplication)
def sra_deleted(sender, instance, **kwargs):
    actor = _get_user_from_instance(instance)
    obj_label = _get_object_display_name(instance)
    log_activity(
        user=actor,
        action=f"Deleted {obj_label}",
        action_type=ActivityLog.ActionType.DELETE,
        obj=instance,
        visibility="public"
    )

@receiver(post_delete, sender=SalesPromotionPermitApplication)
def sppa_deleted(sender, instance, **kwargs):
    actor = _get_user_from_instance(instance)
    obj_label = _get_object_display_name(instance)
    log_activity(
        user=actor,
        action=f"Deleted {obj_label}",
        action_type=ActivityLog.ActionType.DELETE,
        obj=instance,
        visibility="public"
    )

@receiver(post_delete, sender=OrderOfPayment)
def oop_deleted(sender, instance, **kwargs):
    actor = _get_user_from_instance(instance)
    obj_label = _get_object_display_name(instance)
    log_activity(
        user=actor,
        action=f"Deleted {obj_label}",
        action_type=ActivityLog.ActionType.DELETE,
        obj=instance,
        visibility="public"
    )