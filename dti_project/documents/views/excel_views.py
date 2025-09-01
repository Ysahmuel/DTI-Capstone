import datetime
from itertools import chain
from openpyxl import Workbook
from django.http import HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.contrib.auth.decorators import login_required
from ..mixins.permissions_mixins import UserRoleMixin
from ..models import ChecklistEvaluationSheet, InspectionValidationReport, OrderOfPayment, PersonalDataSheet, SalesPromotionPermitApplication, ServiceRepairAccreditationApplication
from ..views.list_views import AllDocumentListView


@login_required
def export_to_excel(request, queryset=None, filename="export.xlsx"):
    """
    Reusable export function that can be called:
    1. As a Django view (Django passes request, queryset=None).
    2. As a helper by passing your own queryset explicitly.
    """

    # If no queryset provided, default to "all documents"
    if queryset is None:
        user = request.user
        sales_promos = UserRoleMixin.get_queryset_or_all(SalesPromotionPermitApplication, user)
        personal_data_sheets = UserRoleMixin.get_queryset_or_all(PersonalDataSheet, user)
        service_accreditations = UserRoleMixin.get_queryset_or_all(ServiceRepairAccreditationApplication, user)
        inspection_reports = UserRoleMixin.get_queryset_or_all(InspectionValidationReport, user)
        orders_of_payment = UserRoleMixin.get_queryset_or_all(OrderOfPayment, user)
        checklist_evaluation_sheets = UserRoleMixin.get_queryset_or_all(ChecklistEvaluationSheet, user)

        queryset = chain(
            sales_promos,
            personal_data_sheets,
            service_accreditations,
            inspection_reports,
            orders_of_payment,
            checklist_evaluation_sheets,
        )

    # Build Excel
    wb = Workbook()
    ws = wb.active
    ws.title = "Export"
    ws.append(["Document Type", "ID", "Filed By", "Date Filed"])

    for doc in queryset:
        doc_type = doc._meta.verbose_name
        doc_id = getattr(doc, "id", "")
        filed_by = getattr(doc, "user", None)
        date_filed = getattr(doc, "date_filed", None) or getattr(doc, "date", "")
        ws.append([doc_type, str(doc_id), str(filed_by), str(date_filed)])

    # Return response
    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = f'attachment; filename={filename}'
    wb.save(response)
    return response
