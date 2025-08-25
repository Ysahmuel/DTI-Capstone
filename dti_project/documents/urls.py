from django.urls import path
from documents import views 

urlpatterns = [
    # CREATE VIEWS
    path("create/sales-promotion", views.CreateSalesPromotionView.as_view(), name="create-sales-promotion"),
    path("create/personal-data-sheet", views.CreatePersonalDataSheetView.as_view(), name="create-personal-data-sheet"),
    path("create/service-repair-accreditation", views.CreateServiceRepairAccreditationApplicationView.as_view(), name="create-service-repair-accreditation"),
    path("create/inspection-validation-report", views.CreateInspectionValidationReportView.as_view(), name="create-inspection-validation-report"),
    path('create/order-of-payment', views.CreateOrderOfPaymentView.as_view(), name="create-order-of-payment"),
    path('create/checklist-evaluation', views.CreateChecklistEvaluationSheetView.as_view(), name='create-checklist-evaluation-sheet'),

    # DETAIL VIEWS
    path("sales-promotion-application/<int:pk>", views.SalesPromotionDetailView.as_view(), name="sales-promotion-application"),
    path("personal-data-sheet/<int:pk>", views.PersonalDataSheetDetailView.as_view(), name="personal-data-sheet"),
    path('service-repair-accreditation/<int:pk>', views.ServiceRepairAccreditationApplicationDetailView.as_view(), name='service-repair-accreditation'),
    path("inspection-validation-report/<int:pk>", views.InspectionValidationReportDetailView.as_view(), name="inspection-validation-report"),
    path("order-of-payment/<int:pk>", views.OrderOfPaymentDetailView.as_view(), name="order-of-payment"),
    path("service-repair-accreditation/<int:pk>/update", views.UpdateServiceRepairAccreditationApplicationView.as_view(), name='update-service-repair-accreditation'),
    path("inspection-validation-report/<int:pk>/update", views.UpdateInspectionValidationReportView.as_view(), name="update-inspection-validation-report"),
    path("order-of-payment/<int:pk>/update", views.UpdateOrderOfPaymentView.as_view(), name="update-order-of-payment"),
    path("checklist-evaluation-sheet/<int:pk>/update", views.UpdateChecklistEvaluationSheetView.as_view(), name='update-checklist-evaluation-sheet')
]