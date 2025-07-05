from django.urls import path
from . import views

urlpatterns = [
    # CREATE VIEWS
    path("create/sales-promotion", views.CreateSalesPromotionView.as_view(), name="create-sales-promotion"),
    path("create/personal-data-sheet", views.CreatePersonalDataSheetView.as_view(), name="create-personal-data-sheet"),

    # DETAIL VIEWS
    path("sales-promotion-application/<int:pk>", views.SalesPromotionDetailView.as_view(), name="sales-promotion-application"),
]