from django.views.generic import ListView
from ..mixins.permissions_mixins import UserRoleMixin
from ..models import ChecklistEvaluationSheet, InspectionValidationReport, OrderOfPayment, PersonalDataSheet, SalesPromotionPermitApplication, ServiceRepairAccreditationApplication

class AllDocumentListView(UserRoleMixin, ListView):
    template_name = 'documents/list_templates/all_documents_list.html'
    context_object_name = 'documents'

    def get_queryset(self):
        return []
    
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

class SalesPromotionListView(ListView):
    pass