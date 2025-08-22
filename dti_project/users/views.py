from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.contrib.auth.views import LoginView, LogoutView
from .forms import CustomLoginForm, CustomUserCreationForm
from django.contrib.auth import login, logout as auth_logout, get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

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

    def form_valid(self, form):
        print("Form is valid, saving user now...")
        user = form.save(commit=False)

        # Ensure user starts as unverified
        user.is_verified = False
        user.save()

        # Generate OTP
        user.generate_secure_otp_code()

        # ✅ log the OTP to console instead of sending email
        print(f"[DEBUG] Verification code for {user.username}: {user.verification_code}")
        logger.info(f"Generated verification code for {user.username}: {user.verification_code}")

        # Store user id in session for modal verification
        self.request.session['pending_verification_user'] = user.id

        return JsonResponse({
            'success': True,
            'message': 'Registration successful! Please enter the verification code.',
            'show_verification': True,
            'masked_email': self.mask_email(user.email)
        })

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

        return context
    

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