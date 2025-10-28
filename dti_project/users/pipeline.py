from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.urls import reverse

User = get_user_model()

def prevent_auto_create(strategy, details, backend, user=None, *args, **kwargs):
    request = strategy.request
    email = details.get('email')

    if not email:
        _add_message_once(request, "Your Google account doesn’t have an email associated.")
        return redirect('sign-in')

    # Case 1: User already linked via Google
    if user:
        if hasattr(user, 'is_verified') and not user.is_verified:
            _add_message_once(request, "Your account is still pending verification. Please verify your email first.")
            return redirect('sign-in')
        return  # allow login

    # Case 2: Try to match with an existing user by email
    try:
        existing_user = User.objects.get(email=email)

        if not getattr(existing_user, 'is_verified', True):
            _add_message_once(request, "Your account is still pending verification. Please verify your email first.")
            return redirect('sign-in')

        # ✅ Account exists & verified: link it to Google
        return {'user': existing_user}

    except User.DoesNotExist:
        # ❌ No user found, block automatic creation
        _add_message_once(request, "No account found for this Google email. Please register first.")
        return redirect(reverse('register'))

def prevent_overwrite_user_details(strategy, details, backend, user=None, *args, **kwargs):
    """
    Prevent Google from overwriting the user's name or profile info
    if the user already exists.
    """
    if user:
        # Remove sensitive fields that you don't want Google to overwrite
        details.pop('first_name', None)
        details.pop('last_name', None)
        details.pop('fullname', None)
        # You can also skip email if you want
        # details.pop('email', None)
    return {'details': details}

def _add_message_once(request, text):
    """Helper to avoid duplicate Django messages."""
    storage = messages.get_messages(request)
    existing = [m.message for m in storage]
    if text not in existing:
        messages.error(request, text)
