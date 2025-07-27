from django.urls import path
from documents import views 

urlpatterns = [
    # CREATE VIEWS
    path("create/sales-promotion", views.CreateSalesPromotionView.as_view(), name="create-sales-promotion"),
    path("create/personal-data-sheet", views.CreatePersonalDataSheetView.as_view(), name="create-personal-data-sheet"),
    path("create/service-repair-accreditation", views.CreateServiceRepairAccreditationApplication.as_view(), name="create-service-repair-accreditation"),
    path("create/inspection-validation-report", views.CreateInspectionValidationReport.as_view(), name="create-inspection-validation-report"),

    # DETAIL VIEWS
    path("sales-promotion-application/<int:pk>", views.SalesPromotionDetailView.as_view(), name="sales-promotion-application"),
    path("personal-data-sheet/<int:pk>", views.PersonalDataSheetDetailView.as_view(), name="personal-data-sheet"),
    path("inspection-validation-report/<int:pk>", views.InspectionValidationReportDetailView.as_view(), name="inspection-validation-report"),
]