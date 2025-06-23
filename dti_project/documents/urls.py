from django.urls import path
from . import views

urlpatterns = [
    path("create_sales_promotion", views.CreateSalesPromotionView.as_view(), name="create-sales-promotion"),
]