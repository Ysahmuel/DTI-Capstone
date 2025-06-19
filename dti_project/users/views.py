from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.contrib.auth.views import LoginView, LogoutView
from .forms import CustomUserCreationForm
from django.contrib.auth import login, logout as auth_logout

# Create your views here.
class CustomLoginView(LoginView):
    template_name = 'users/login.html'
    redirect_authenticated_user = True
    
    def get_success_url(self) -> str:
        return reverse_lazy('dashboard')
    
    
class CustomRegisterView(CreateView):
    template_name = 'users/register.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        return context
