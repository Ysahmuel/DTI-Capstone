from django.urls import path
from . import views

path("", views.DocumentListView.as_view(), name="documents")