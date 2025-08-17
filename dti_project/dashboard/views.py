from django.shortcuts import render
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from documents.models import ChecklistEvaluationSheet, InspectionValidationReport, OrderOfPayment, PersonalDataSheet, SalesPromotionPermitApplication, ServiceRepairAccreditationApplication
from django.db.models import Value
from django.db.models.functions import Concat
    
# Create your views here.
class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "dashboard/dashboard.html"

    @staticmethod
    def get_queryset_or_all(model, user):
        qs = model.objects.all() if user.role == 'admin' else model.objects.filter(user=user)
        
        return qs.only('pk', 'id')  # Add other fields that __str__ methods need

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        context.update({
            'sales_promos': self.get_queryset_or_all(SalesPromotionPermitApplication, user),
            'personal_data_sheets': self.get_queryset_or_all(PersonalDataSheet, user),
            'service_accreditations': self.get_queryset_or_all(ServiceRepairAccreditationApplication, user),
            'inspection_reports': self.get_queryset_or_all(InspectionValidationReport, user),
            'orders_of_payment': self.get_queryset_or_all(OrderOfPayment, user),
            'checklist_evaluation_sheets': self.get_queryset_or_all(ChecklistEvaluationSheet, user),
        })

        return context