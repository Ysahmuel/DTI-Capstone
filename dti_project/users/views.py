from django.shortcuts import render
from django.views.generic import CreateView

# Create your views here.
class CustomRegisterView(CreateView):
    template_name = 'users/register.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        return context
