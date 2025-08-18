from django.urls import path
from . import views

urlpatterns = [
    path('', views.DashboardView.as_view(), name="dashboard"),
    path('search-suggestions/', views.SearchSuggestionsView.as_view(), name='search_suggestions'),
]