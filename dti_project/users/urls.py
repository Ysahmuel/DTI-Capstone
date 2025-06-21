from django.urls import path
from . import views

urlpatterns = [
    path('sign-in', views.CustomLoginView.as_view(), name="sign-in"),
    path('register', views.CustomRegisterView.as_view(), name="register"),
    path('logout', views.logout, name="logout")
]