import datetime
from django.views.generic import ListView
from ..mixins.filter_mixins import FilterableDocumentMixin
from ..mixins.counter_mixins import DocumentCountMixin
from ..mixins.permissions_mixins import UserRoleMixin
from ..models import ChecklistEvaluationSheet, InspectionValidationReport, OrderOfPayment, PersonalDataSheet, SalesPromotionPermitApplication, ServiceRepairAccreditationApplication
from itertools import chain
from operator import attrgetter
from django.db.models import Q

def get_date_field(obj):
    """Return the date field (date_filed or date) for any document."""
    return getattr(obj, "date_filed", None) or getattr(obj, "date", None) or datetime.date.min

class BaseDocumentListView(UserRoleMixin, DocumentCountMixin, FilterableDocumentMixin, ListView):
    """
    Generic list view for document models.
    Just set `model`, `template_name`, `context_object_name`, and `active_doc_type`.
    """
    active_doc_type = None  # override in subclasses

    def get_queryset(self):
        user = self.request.user
        qs = self.get_queryset_or_all(self.model, user)
        qs = self.apply_filters(qs)
        return sorted(qs, key=get_date_field, reverse=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["documents"] = self.get_queryset()
        context["active_doc_type"] = self.active_doc_type
        return context


class AllDocumentListView(UserRoleMixin, DocumentCountMixin, FilterableDocumentMixin, ListView):
    template_name = "documents/list_templates/all_documents_list.html"
    context_object_name = "documents"

    def get_queryset(self):
        user = self.request.user

        sales_promos = self.get_queryset_or_all(SalesPromotionPermitApplication, user)
        personal_data_sheets = self.get_queryset_or_all(PersonalDataSheet, user)
        service_accreditations = self.get_queryset_or_all(ServiceRepairAccreditationApplication, user)
        inspection_reports = self.get_queryset_or_all(InspectionValidationReport, user)
        orders_of_payment = self.get_queryset_or_all(OrderOfPayment, user)
        checklist_evaluation_sheets = self.get_queryset_or_all(ChecklistEvaluationSheet, user)

        # Apply filters per queryset
        combined = chain(
            self.apply_filters(sales_promos),
            self.apply_filters(personal_data_sheets),
            self.apply_filters(service_accreditations),
            self.apply_filters(inspection_reports),
            self.apply_filters(orders_of_payment),
            self.apply_filters(checklist_evaluation_sheets),
        )

        documents = sorted(combined, key=get_date_field, reverse=True)
        return documents

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        context.update({
            "sales_promos": self.apply_filters(self.get_queryset_or_all(SalesPromotionPermitApplication, user)),
            "personal_data_sheets": self.apply_filters(self.get_queryset_or_all(PersonalDataSheet, user)),
            "service_accreditations": self.apply_filters(self.get_queryset_or_all(ServiceRepairAccreditationApplication, user)),
            "inspection_reports": self.apply_filters(self.get_queryset_or_all(InspectionValidationReport, user)),
            "orders_of_payment": self.apply_filters(self.get_queryset_or_all(OrderOfPayment, user)),
            "checklist_evaluation_sheets": self.apply_filters(self.get_queryset_or_all(ChecklistEvaluationSheet, user)),
            "documents": self.get_queryset(),
        })

        return context

class SalesPromotionListView(BaseDocumentListView):
    model = SalesPromotionPermitApplication
    template_name = "documents/list_templates/sales_promotion_list.html"
    context_object_name = "sales_promos"
    active_doc_type = "sales_promos"


class PersonalDataSheetListView(BaseDocumentListView):
    model = PersonalDataSheet
    template_name = "documents/list_templates/personal_data_sheet_list.html"
    context_object_name = "personal_data_sheets"
    active_doc_type = "personal_data_sheets"


class ServiceRepairAccreditationApplicationListView(BaseDocumentListView):
    model = ServiceRepairAccreditationApplication
    template_name = "documents/list_templates/service_repair_list.html"
    context_object_name = "service_accreditations"
    active_doc_type = "service_accreditations"


class InspectionValidationReportListView(BaseDocumentListView):
    model = InspectionValidationReport
    template_name = "documents/list_templates/inspection_validation_report_list.html"
    context_object_name = "inspection_reports"
    active_doc_type = "inspection_reports"


class OrderOfPaymentListView(BaseDocumentListView):
    model = OrderOfPayment
    template_name = "documents/list_templates/order_of_payment_list.html"
    context_object_name = "orders_of_payment"
    active_doc_type = "orders_of_payment"


class ChecklistEvaluationSheetListView(BaseDocumentListView):
    model = ChecklistEvaluationSheet
    template_name = "documents/list_templates/checklist_evaluation_list.html"
    context_object_name = "checklist_evaluation_sheets"
    active_doc_type = "checklist_evaluation_sheets"
