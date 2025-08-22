from django.urls import path
from . import views

urlpatterns = [
    path('sign-in/', views.CustomLoginView.as_view(), name="sign-in"),
    path('register/', views.CustomRegisterView.as_view(), name="register"),
    path('verify-user/', views.VerifyUserView.as_view(), name='verify-user'),
    path('resend-code/', views.ResendCodeView.as_view(), name='resend-code'),
    path('logout/', views.logout, name="logout"),
]

htmxpatterns = [
    path('check_email_exists', views.check_email_exists, name="check-email-exists"),
    path('check_password_strength', views.check_password_strength, name='check-password-strength')
]

urlpatterns += htmxpatterns