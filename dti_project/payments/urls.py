from django.urls import path
from . import views

urlpatterns = [
    path("pay/<str:doc_type>/<int:pk>/", views.payment_page, name="payment-page"),
    path("success/<str:doc_type>/<int:pk>/", views.payment_success, name="payment-success"),
    path("failed/", views.payment_failed, name="payment-failed"),
    path("verify/<str:doc_type>/<int:pk>/", views.verify_payment, name="verify-payment"),
    path("receipt/<str:doc_type>/<int:pk>/", views.download_receipt, name="download-receipt"),
]