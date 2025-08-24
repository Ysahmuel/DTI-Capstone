from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, View
from django.contrib.auth.views import LoginView, LogoutView
from .models import User
from .forms import CustomLoginForm, CustomUserCreationForm
from django.contrib.auth import login, logout as auth_logout, get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.contrib import messages
import logging

logger = logging.getLogger(__name__)

# Create your views here.
class CustomLoginView(LoginView):
    template_name = 'users/login.html'
    redirect_authenticated_user = True
    authentication_form = CustomLoginForm
    
    def get_success_url(self) -> str:
        return reverse_lazy('dashboard')
    
class CustomRegisterView(CreateView):
    template_name = 'users/register.html'
    redirect_authenticated_user = True
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('dashboard')

    def post(self, request, *args, **kwargs):
        print("=== POST METHOD CALLED ===")
        print(f"Is AJAX: {request.headers.get('X-Requested-With') == 'XMLHttpRequest'}")
        print(f"POST data: {dict(request.POST)}")
        
        # Handle AJAX requests
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            form = self.get_form()
            print(f"Form created: {form}")
            print(f"Form is valid: {form.is_valid()}")
            
            if not form.is_valid():
                print(f"Form errors: {form.errors}")
                print(f"Form non-field errors: {form.non_field_errors()}")
            
            if form.is_valid():
                return self.form_valid(form)
            else:
                return self.form_invalid(form)
        
        # Handle normal form submissions (fallback)
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        print("=== FORM_VALID CALLED ===")
        user = form.save(commit=False)

        # Ensure user starts as unverified
        user.is_verified = False
        user.save()
        print(f"User saved: {user.username}")

        # Generate OTP
        user.generate_secure_otp_code()

        # ✅ log the OTP to console instead of sending email
        print(f"[DEBUG] Verification code for {user.username}: {user.verification_code}")

        # Store user id in session for modal verification
        self.request.session['pending_verification_user'] = user.id

        # Return JSON response for AJAX requests
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': 'Registration successful! Please enter the verification code.',
                'show_verification': True,
                'masked_email': self.mask_email(user.email)
            })
        
        # Fallback for normal requests
        return super().form_valid(form)

    def form_invalid(self, form):
        print("=== FORM_INVALID CALLED ===")
        print(f"All form errors: {form.errors}")

        # Add error messages to Django messages
        for field, error_list in form.errors.items():
            for error in error_list:
                if field == '__all__':
                    messages.error(self.request, f"{error}")
                else:
                    field_name = field.replace('_', ' ').title()
                    messages.error(self.request, f"{field_name}: {error}")

        # AJAX response (minimal, since frontend will display Django messages)
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False}, status=400)

        return super().form_invalid(form)
    
    @staticmethod
    def mask_email(email):
        """Mask email for display"""
        if '@' not in email:
            return email
        username, domain = email.split('@', 1)
        if len(username) <= 2:
            masked_username = '*' * len(username)
        else:
            masked_username = username[:2] + '*' * (len(username) - 2)
        return f"{masked_username}@{domain}"
    

class VerifyUserView(View):
    """Handles OTP verification separately"""

    def post(self, request, *args, **kwargs):
        user_id = request.session.get('pending_verification_user')
        if not user_id:
            return JsonResponse({'success': False, 'error': 'No pending verification'}, status=400)

        user = get_object_or_404(User, id=user_id)

        # Get code from request
        code = request.POST.get('verification_code') or request.POST.get('code', '')

        if not code:
            digits = [request.POST.get(f'digit_{i}', '') for i in range(1, 7)]
            code = ''.join(digits)

        if not code or len(code) != 6:
            return JsonResponse({'success': False, 'error': 'Please enter a valid 6-digit code'}, status=400)

        # Verify
        if user.is_verification_code_valid(code):
            user.is_verified = True
            user.verification_code = None
            user.verification_code_expiration_date = None
            user.save()

            login(request, user)
            del request.session['pending_verification_user']

            return JsonResponse({
                'success': True,
                'message': 'Verification successful!',
                'redirect': reverse('dashboard')
            })
        else:
            return JsonResponse({'success': False, 'error': 'Invalid or expired verification code'}, status=400)

class ResendCodeView(View):
    """Handles resending OTP"""

    def post(self, request, *args, **kwargs):
        user_id = request.session.get('pending_verification_user')
        if not user_id:
            return JsonResponse({'success': False, 'error': 'No pending verification'}, status=400)

        user = get_object_or_404(User, id=user_id)
        user.generate_secure_otp_code()

        # ✅ log it to terminal
        print(f"[DEBUG] Resent verification code for {user.username}: {user.verification_code}")

        return JsonResponse({
            'success': True,
            'message': 'Verification code resent!'
        })

# ---------------------- FUNCTION BASED VIEWS --------------------------- #    

def logout(request):
    auth_logout(request)
    return HttpResponseRedirect("/")

def check_email_exists(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        if email:
            if get_user_model().objects.filter(email=email).exists():
                return HttpResponse('<span style="color: red;">This email already exists</span>')
            else:
                return HttpResponse('<span style="color: green;">Email is available</span>')
    return HttpResponse("")

def check_password_strength(request):
    password = request.POST.get('password1', "")
    try:
        validate_password(password)
        html = '<span id="message-success" style="color: green;">Strong password</span>'
        response = HttpResponse(html)
        response['HX-Trigger'] = 'passwordValid'
        return response
    except ValidationError as e:
        error_spans = "".join(
            f'<span id="message-error" style="color:red; display:block;">{msg}</span>'
            for msg in e.messages
        )
        response = HttpResponse(error_spans)
        response['HX-Trigger'] = 'passwordInvalid'
        return response
    
def check_passwords_match(request):
    pass