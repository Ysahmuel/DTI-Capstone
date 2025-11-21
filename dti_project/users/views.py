from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, ListView, DetailView, UpdateView, TemplateView, View
from django.contrib.auth.views import LoginView
from django.contrib.auth import login, logout as auth_logout, get_user_model
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.contrib import messages
import logging

from users.mixins import FormSubmissionMixin
from users.models import User
from .forms import CustomLoginForm, CustomUserCreationForm
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import get_user_model
from .forms import AddStaffForm
from django.http import JsonResponse
from django.contrib import messages
from django.shortcuts import redirect
from django.contrib.auth import get_user_model
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from django.db import IntegrityError
import random, string
from .forms import AddStaffForm
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.utils import timezone 
from .forms import AddStaffForm

from documents.models import (
    # Base models
    BaseApplication,
    DraftModel,
    YesNoField,
    PeriodModel,
    
    # Checklist evaluation
    ChecklistEvaluationSheet,
    
    # Inspection validation
    InspectionValidationReport,
    
    # Order of payment
    OrderOfPayment,
    
    # Personal data sheet models
    PersonalDataSheet,
    EmployeeBackground,
    TrainingsAttended,
    EducationalAttainment,
    CharacterReference,
    
    # Sales promotion models
    SalesPromotionPermitApplication,
    ProductCovered,
    
    # Service repair accreditation models
    ServiceRepairAccreditationApplication,
    Service,
    ServiceCategory,
)

logger = logging.getLogger(__name__)

# Create your views here.
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import User
from documents.verification import VerificationDocument


def verify_account_upload(request, user_id):
    user = get_object_or_404(User, pk=user_id)

    if request.method == "POST":
        files = request.FILES.getlist("files")
        if len(files) < 2:
            messages.error(request, "Please upload at least 2 files to verify your account.")
            return redirect("settings")

        # Save uploaded files
        for f in files:
            VerificationDocument.objects.create(
                user=user,
                file=f
            )

        messages.success(request, "Documents uploaded successfully. Awaiting admin verification.")
        return redirect("settings")

    return redirect("settings")



# verify account admin side
# users/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, View
from django.contrib.auth import get_user_model

User = get_user_model()


# --- List all business owners (verified + unverified) ---
from django.views.generic import ListView
from users.models import User  # make sure this is your custom user model

# --- List all business owners (verified + unverified) ---
from django.views.generic import ListView
from users.models import User

class BusinessOwnerListView(ListView):
    model = User
    template_name = 'users/bo_accounts.html'
    context_object_name = 'businesshumans'

    def get_queryset(self):
        # Return both verified and unverified business owners
        return User.objects.filter(
            role__in=['unverified_owner', 'business_owner']
        ).order_by('-date_joined')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['businesshumans'] = self.get_queryset()  # keep naming consistent
        context['user_type'] = 'business_owner'
        return context




# --- View verification request (admin sees uploaded documents) ---
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from .models import User
from notifications.models import Notification


def view_verification(request, user_id):
    user = get_object_or_404(User, pk=user_id)

    if request.method == "POST":
        action = request.POST.get("action")  # <-- indented correctly

        if action == "verify":
            user.role = User.Roles.BUSINESS_OWNER
            user.save()

            # Send notification to the user
            Notification.objects.create(
                user=user,
                sender=request.user,  # admin who verified
                message="Your account has been verified successfully.",
                type="approved",
                url=None
            )

            messages.success(request, f"{user.get_full_name()} has been verified successfully.")
            return redirect("bo_accounts")

        elif action == "deny":
            user.role = User.Roles.UNVERIFIED_OWNER
            user.save()

            # Send notification to the user
            Notification.objects.create(
                user=user,
                sender=request.user,  # admin who denied
                message="Your verification documents were rejected as invalid.",
                type="rejected",
                url=None
            )

            messages.warning(request, f"{user.get_full_name()}\'s documents were denied.")
            return redirect("bo_accounts")




# One-click verify user
class VerifyUserView(View):
    def get(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        user.role = User.Roles.BUSINESS_OWNER
        user.is_verified = True
        user.save()
        # Optional: mark any VerificationRequest as verified
        VerificationRequest.objects.filter(user=user).update(is_verified=True, admin_verified_at=timezone.now(), admin_verified_by=request.user)
        return redirect('bo_accounts')



#forgot password view
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib import messages
from django.contrib.auth import login
from django.urls import reverse
from .forms import ForgotPasswordForm, ResetPasswordForm
from .models import User  # adjust if your User model is custom
import random

# -----------------------------
# FORGOT PASSWORD
# -----------------------------
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt



class ForgotPasswordView(View):
    template_name = 'users/forgot_password.html'

    def get(self, request):
        form = ForgotPasswordForm()
        return render(request, self.template_name, {
            'form': form,
            'verification_type': 'reset_password',
            'verification_sent': False
        })

    def post(self, request):
        form = ForgotPasswordForm(request.POST)
        is_ajax = request.headers.get("x-requested-with") == "XMLHttpRequest"

        if not form.is_valid():
            if is_ajax:
                return JsonResponse({
                    "success": False,
                    "error": "Invalid email format."
                })
            return render(request, self.template_name, {
                'form': form,
                'verification_type': 'reset_password',
                'verification_sent': False
            })

        email = form.cleaned_data['email']
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            if is_ajax:
                return JsonResponse({
                    "success": False,
                    "error": "Email not found."
                })
            messages.error(request, "Email not found.")
            return render(request, self.template_name, {
                'form': form,
                'verification_type': 'reset_password',
                'verification_sent': False
            })

        # ✅ Generate OTP and store
        user.generate_secure_otp_code()
        user.save()

        # ✅ Save info to session
        request.session['pending_verification_user'] = user.id
        request.session['reset_email'] = user.email

        # ✅ Debug log
        print(f"[DEBUG] Password reset code for {email}: {user.verification_code}")

        # ✅ Masked email (e.g., "te***@gmail.com")
        def mask_email(email):
            username, domain = email.split('@')
            masked_username = username[0] + "***" + username[-1] if len(username) > 2 else username[0] + "***"
            return f"{masked_username}@{domain}"

        if is_ajax:
            return JsonResponse({
                "success": True,
                "masked_email": mask_email(email)
            })

        # For normal form POST (fallback)
        return render(request, self.template_name, {
            'form': form,
            'verification_type': 'reset_password',
            'verification_sent': True,
            'email': email
        })


# -----------------------------
# RESET PASSWORD
# -----------------------------
from django.views import View
from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.urls import reverse

User = get_user_model()

class ResetPasswordView(View):
    template_name = 'users/reset_password.html'

    def get(self, request):
        email = request.session.get('reset_email')
        if not email:
            messages.error(request, "Your session has expired. Please restart the password reset process.")
            return redirect('forgot_password')
        return render(request, self.template_name)

    def post(self, request):
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        email = request.session.get('reset_email')

        if not email:
            return JsonResponse({
                'success': False,
                'message': 'Session expired. Please restart the password reset process.'
            })

        if not password or not confirm_password:
            return JsonResponse({
                'success': False,
                'message': 'Please fill out both password fields.'
            })

        if password != confirm_password:
            return JsonResponse({
                'success': False,
                'message': 'Passwords do not match.'
            })

        if len(password) < 8:
            return JsonResponse({
                'success': False,
                'message': 'Password must be at least 8 characters long.'
            })

        try:
            user = User.objects.get(email=email)
            user.password = make_password(password)
            user.save()

            # ✅ Clean up session and add success message
            request.session.pop('reset_email', None)
            request.session.pop('pending_verification_user', None)

            messages.success(request, "Your password has been successfully reset! You can now sign in.")

            return JsonResponse({
                'success': True,
                'redirect': reverse('sign-in')
            })

        except User.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'No user account found for this email.'
            })



#add staff view
User = get_user_model()


def add_staff(request):
    if request.method == 'POST':
        form = AddStaffForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            address = form.cleaned_data.get('default_address', '')
            phone = form.cleaned_data.get('default_phone', '')
            birthday = form.cleaned_data.get('birthday')

            today = timezone.localdate()
            if birthday >= today:
                form.add_error('birthday', 'Birthday must be in the past.')
                return render(request, 'users/add_staff.html', {'form': form})

            # Generate unique email
            base_email = f"{last_name.lower()}.dti.agent@gmail.com"
            email = base_email
            counter = 1
            while User.objects.filter(email=email).exists():
                email = f"{last_name.lower()}{counter}.dti.agent@gmail.com"
                counter += 1

            username = email.split('@')[0]

            # 🔐 Generate password in the format LastnameYYYYMMDD
            formatted_birthday = birthday.strftime("%Y%m%d")
            password = f"{last_name.capitalize()}{formatted_birthday}"

            user = User.objects.create_user(
                username=username,
                first_name=first_name,
                last_name=last_name,
                email=email,
                password=password,
                role='collection_agent',
                is_staff=True,
            )

            user.default_address = address
            user.default_phone = phone
            user.birthday = birthday
            user.save()

            return render(request, 'users/add_staff.html', {
                'form': AddStaffForm(),
                'show_popup': True,
                'popup_email': email,
                'popup_password': password,
                'user_id': user.id,
            })
    else:
        form = AddStaffForm()

    return render(request, 'users/add_staff.html', {'form': form})





# Staff Created Popup View
from django.shortcuts import render

def staff_created_popup(request):
    email = request.session.get('new_staff_email')
    password = request.session.get('new_staff_password')

    context = {
        'email': email,
        'password': password,
    }

    return render(request, 'users/staff_created_popup.html', context)

# Delete New Staff View

User = get_user_model()

def delete_new_staff(request, user_id):
    """Delete the newly created staff account."""
    try:
        User.objects.filter(id=user_id).delete()
        messages.success(request, "Newly created account deleted.")
    except Exception as e:
        messages.error(request, f"Error deleting account: {e}")
    return redirect('staff_accounts')






#Settings View
class SettingsView(LoginRequiredMixin, TemplateView):
    template_name = "users/settings.html"

#Profile Detail View
class ProfileDetailView(DetailView):
    model = User
    template_name = "users/profile.html"
    context_object_name = "profile"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile = self.get_object()

        # Document queries
        sales_promos = SalesPromotionPermitApplication.objects.filter(user=profile)
        personal_data_sheets = PersonalDataSheet.objects.filter(user=profile)
        service_accreditations = ServiceRepairAccreditationApplication.objects.filter(user=profile)
        inspection_reports = InspectionValidationReport.objects.filter(user=profile)
        orders_of_payment = OrderOfPayment.objects.filter(user=profile)
        checklist_evaluation_sheets = ChecklistEvaluationSheet.objects.filter(user=profile)

        # Total count
        total_documents = (
            sales_promos.count()
            + personal_data_sheets.count()
            + service_accreditations.count()
            + inspection_reports.count()
            + orders_of_payment.count()
            + checklist_evaluation_sheets.count()
        )

        # Add to context
        context.update({
            "sales_promos": sales_promos,
            "personal_data_sheets": personal_data_sheets,
            "service_accreditations": service_accreditations,
            "inspection_reports": inspection_reports,
            "orders_of_payment": orders_of_payment,
            "checklist_evaluation_sheets": checklist_evaluation_sheets,
            "total_documents": total_documents,
        })
        return context

class StaffListView(ListView):
    model = User
    template_name = 'users/staff_accounts.html'
    
    def get_queryset(self):
        qs = User.objects.filter(role='collection_agent')

        return qs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'users': self.get_queryset(),
            'user_type': 'staff'
        })
        return context
    

#Profile Edit View
from .forms import ProfileEditForm

class ProfileEditView(UpdateView):
    model = User
    form_class = ProfileEditForm
    template_name = "users/profile_edit.html"
    context_object_name = "profile"

    def get_success_url(self):
        return reverse_lazy('profile', kwargs={'pk': self.object.pk})




class CustomLoginView(FormSubmissionMixin, LoginView):
    template_name = 'users/login.html'
    redirect_authenticated_user = True
    authentication_form = CustomLoginForm
    
    def get_success_url(self) -> str:
        return reverse_lazy('dashboard')
    
class CustomRegisterView(FormSubmissionMixin, CreateView):
    template_name = 'users/register.html'
    redirect_authenticated_user = True
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('dashboard')

    def post(self, request, *args, **kwargs):
        print("=== POST METHOD CALLED ===")
        print(f"Is AJAX: {request.headers.get('X-Requested-With') == 'XMLHttpRequest'}")
        print(f"POST data: {dict(request.POST)}")
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            form = self.get_form()
            if form.is_valid():
                return self.form_valid(form)
            else:
                return self.form_invalid(form)

        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        print("=== FORM_VALID CALLED ===")
        user = form.save(commit=False)
        user.is_verified = False
        user.save()

        user.generate_secure_otp_code()
        print(f"[DEBUG] Verification code for {user.username}: {user.verification_code}")

        self.request.session['pending_verification_user'] = user.id

        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'verification_type': 'registration',
                'message': 'Registration successful! Please enter the verification code.',
                'show_verification': True,
                'masked_email': self.mask_email(user.email),
            })

        return super().form_valid(form)

    @staticmethod
    def mask_email(email):
        if '@' not in email:
            return email
        username, domain = email.split('@', 1)
        masked_username = username[:2] + '*' * (len(username) - 2) if len(username) > 2 else '*' * len(username)
        return f"{masked_username}@{domain}"

    

class VerifyUserView(View):
    def post(self, request, *args, **kwargs):
        user_id = request.session.get('pending_verification_user')
        if not user_id:
            return JsonResponse({'success': False, 'error': 'No pending verification'}, status=400)

        user = get_object_or_404(User, id=user_id)
        code = request.POST.get('code') or request.POST.get('verification_code', '')

        if not code or len(code) != 6:
            return JsonResponse({'success': False, 'error': 'Please enter a valid 6-digit code'}, status=400)

        if user.is_verification_code_valid(code):
            user.is_verified = True
            user.verification_code = None
            user.verification_code_expiration_date = None
            user.save()

            verification_type = request.POST.get('verification_type', '')

            if verification_type == 'reset_password':
                # For forgot password → reset flow
                request.session['reset_email'] = user.email
                del request.session['pending_verification_user']  # 🟢 clean session
                return JsonResponse({
                    'success': True,
                    'message': 'Verification successful!',
                    'redirect': reverse('reset_password')
                })
            else:
                # For normal registration flow
                login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                del request.session['pending_verification_user']
                return JsonResponse({
                    'success': True,
                    'message': 'Verification successful!',
                    'redirect': reverse('dashboard')
                })

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