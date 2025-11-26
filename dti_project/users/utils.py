from .models import ActivityLog
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.signals import user_logged_in, user_logged_out, user_login_failed
from django.dispatch import receiver
from user_agents import parse

def get_user_agent_info(user_agent_string):
    """Parse user agent to extract browser/device info"""
    try:
        ua = parse(user_agent_string or "")
        return f"{ua.browser.family} {ua.browser.version_string} on {ua.os.family}"
    except Exception:
        return (user_agent_string or "")[:200] if user_agent_string else "Unknown"

def log_activity(user=None, action="", action_type="page_view", obj=None, ip=None, user_agent=None, extra=None, visibility="private"):
    """
    Create ActivityLog entry with clean action text.
    action: human-readable short string (e.g. "Approved SRA #44", "Logged in")
    """
    ct = None
    oid = None
    if obj is not None:
        try:
            ct = ContentType.objects.get_for_model(obj.__class__)
            oid = getattr(obj, "pk", None) or getattr(obj, "id", None)
            if oid is not None:
                oid = str(oid)
        except Exception:
            ct = None
            oid = None

    role = getattr(user, "role", None) if user else None
    ua = get_user_agent_info(user_agent) if user_agent else None

    ActivityLog.objects.create(
        user=user,
        role=role,
        action_type=action_type,
        action=action[:500],
        content_type=ct,
        object_id=oid,
        ip_address=ip,
        user_agent=ua,
        extra=extra or {},
        visibility=visibility
    )

# ============================================
# AUTHENTICATION EVENTS
# ============================================
@receiver(user_logged_in)
def _on_user_logged_in(sender, request, user, **kwargs):
    log_activity(
        user=user,
        action="Logged in",
        action_type=ActivityLog.ActionType.LOGIN,
        ip=request.META.get("HTTP_X_FORWARDED_FOR", request.META.get("REMOTE_ADDR")),
        user_agent=request.META.get("HTTP_USER_AGENT"),
        visibility="public"
    )

@receiver(user_logged_out)
def _on_user_logged_out(sender, request, user, **kwargs):
    log_activity(
        user=user,
        action="Logged out",
        action_type=ActivityLog.ActionType.LOGOUT,
        ip=(request.META.get("HTTP_X_FORWARDED_FOR", request.META.get("REMOTE_ADDR")) if request else None),
        user_agent=(request.META.get("HTTP_USER_AGENT") if request else None),
        visibility="public"
    )

@receiver(user_login_failed)
def _on_user_login_failed(sender, credentials, request, **kwargs):
    email = credentials.get("username") or credentials.get("email") or "unknown"
    log_activity(
        user=None,
        action=f"Failed login attempt for email {email}",
        action_type=ActivityLog.ActionType.LOGIN_FAILED,
        ip=(request.META.get("HTTP_X_FORWARDED_FOR", request.META.get("REMOTE_ADDR")) if request else None),
        user_agent=(request.META.get("HTTP_USER_AGENT") if request else None),
        extra={"attempted_email": email},
        visibility="admin"
    )