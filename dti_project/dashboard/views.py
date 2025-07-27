from django.shortcuts import render
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from documents.models import InspectionValidationReport, PersonalDataSheet, SalesPromotionPermitApplication

# Create your views here.
class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "dashboard/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context.update({
            'sales_promos': SalesPromotionPermitApplication.objects.all(),
            'personal_data_sheets': PersonalDataSheet.objects.all(),
            'inspection_reports': InspectionValidationReport.objects.all(),
        })

        return context