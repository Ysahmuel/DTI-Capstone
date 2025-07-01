from django.urls import path
from . import views

urlpatterns = [
    path("create/sales-promotion", views.CreateSalesPromotionView.as_view(), name="create-sales-promotion"),
    path("sales-promotion-application/<int:pk>", views.SalesPromotionDetailView.as_view(), name="sales-promotion-application"),
]