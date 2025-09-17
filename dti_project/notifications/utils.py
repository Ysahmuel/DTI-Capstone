from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

def send_user_notification(user_id, notification):
    channel_layer = get_channel_layer()

    if hasattr(notification, "display_message"):
        payload = {
            "id": int(notification.id),
            "message": str(notification.display_message()),
            "time": str(notification.time_display()),
            "url": str(notification.url) if notification.url else "",
            "type": str(notification.type),
            "is_read": bool(notification.is_read),
            "sender_image": (
                str(notification.sender.profile_picture.url)
                if notification.sender and getattr(notification.sender, "profile_picture", None)
                else None
            ),
        }
    else:
        payload = notification

    async_to_sync(channel_layer.group_send)(
        f"notifications_{user_id}",   # fixed underscore
        {
            "type": "notification.message",   # matches consumer method
            "content": payload,
        }
    )