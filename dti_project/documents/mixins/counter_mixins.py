from ..models import ChecklistEvaluationSheet, InspectionValidationReport, OrderOfPayment, PersonalDataSheet, SalesPromotionPermitApplication, ServiceRepairAccreditationApplication


class DocumentCountMixin:
    def get_document_counts(self, user):
        return {
            'sales_promos_count': self.get_count_or_all(SalesPromotionPermitApplication, user),
            'personal_data_sheets_count': self.get_count_or_all(PersonalDataSheet, user),
            'service_accreditations_count': self.get_count_or_all(ServiceRepairAccreditationApplication, user),
            'inspection_reports_count': self.get_count_or_all(InspectionValidationReport, user),
            'orders_of_payment_count': self.get_count_or_all(OrderOfPayment, user),
            'checklist_evaluation_sheets_count': self.get_count_or_all(ChecklistEvaluationSheet, user),
        }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context.update(self.get_document_counts(user))
        return context