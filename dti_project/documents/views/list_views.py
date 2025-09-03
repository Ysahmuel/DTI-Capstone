import datetime
from django.views.generic import ListView
from ..mixins.counter_mixins import DocumentCountMixin
from ..mixins.permissions_mixins import UserRoleMixin
from ..models import ChecklistEvaluationSheet, InspectionValidationReport, OrderOfPayment, PersonalDataSheet, SalesPromotionPermitApplication, ServiceRepairAccreditationApplication
from itertools import chain
from operator import attrgetter

class AllDocumentListView(UserRoleMixin, DocumentCountMixin, ListView):
    template_name = 'documents/list_templates/all_documents_list.html'
    context_object_name = 'documents'

    def get_queryset(self):
        user = self.request.user

        sales_promos = self.get_queryset_or_all(SalesPromotionPermitApplication, user)
        personal_data_sheets = self.get_queryset_or_all(PersonalDataSheet, user)
        service_accreditations = self.get_queryset_or_all(ServiceRepairAccreditationApplication, user)
        inspection_reports = self.get_queryset_or_all(InspectionValidationReport, user)
        orders_of_payment = self.get_queryset_or_all(OrderOfPayment, user)
        checklist_evaluation_sheets = self.get_queryset_or_all(ChecklistEvaluationSheet, user)

        # combine them into one iterable
        combined = chain(
            sales_promos,
            personal_data_sheets,
            service_accreditations,
            inspection_reports,
            orders_of_payment,
            checklist_evaluation_sheets
        )

        def get_date(obj):
            return getattr(obj, 'date_filed', None) or getattr(obj, 'date', None) or datetime.date.min

        documents = sorted(combined, key=get_date, reverse=True)
        return documents
    
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
            'documents': self.get_queryset()
        })

        return context


class SalesPromotionListView(UserRoleMixin, DocumentCountMixin, ListView):
    model = SalesPromotionPermitApplication
    template_name = 'documents/list_templates/sales_promotion_list.html'
    context_object_name = 'sales_promos'

    def get_queryset(self):
        user = self.request.user

        sales_promos = self.get_queryset_or_all(SalesPromotionPermitApplication, user)

        def get_date(obj):
            return getattr(obj, 'date_filed', None) or getattr(obj, 'date', None) or datetime.date.min

        documents = sorted(sales_promos, key=get_date, reverse=True)
        return documents
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['documents'] = self.get_queryset()

        return context
    
class PersonalDataSheetListView(UserRoleMixin, DocumentCountMixin, ListView):
    model = PersonalDataSheet
    template_name = 'documents/list_templates/personal_data_sheet_list.html'
    context_object_name = 'personal_data_sheets'

    def get_queryset(self):
        user = self.request.user

        personal_data_sheets = self.get_queryset_or_all(PersonalDataSheet, user)

        def get_date(obj):
            return getattr(obj, 'date_filed', None) or getattr(obj, 'date', None) or datetime.date.min

        documents = sorted(personal_data_sheets, key=get_date, reverse=True)
        return documents
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['documents'] = self.get_queryset()

        return context