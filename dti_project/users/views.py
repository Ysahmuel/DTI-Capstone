from django.http import HttpResponseRedirect
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
    redirect_authenticated_user = True
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('dashboard')

    def form_valid(self, form):
        print("Form is valid, saving user now...")
        response = super().form_valid(form)
        user = form.save()

        print(f"User created: {user}")
        login(self.request, user)
        
        return response
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        return context
    

def logout(request):
    auth_logout(request)
    return HttpResponseRedirect("/")