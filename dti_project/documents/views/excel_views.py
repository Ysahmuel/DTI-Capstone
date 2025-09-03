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
from django.db.models import Q
from urllib.parse import quote

class ImportFromExcelView(View):
    pass

import datetime
from itertools import chain
from urllib.parse import quote
from openpyxl import Workbook
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Min, Max

from ..mixins.permissions_mixins import UserRoleMixin
from ..models import (
    ChecklistEvaluationSheet,
    InspectionValidationReport,
    OrderOfPayment,
    PersonalDataSheet,
    SalesPromotionPermitApplication,
    ServiceRepairAccreditationApplication,
)


@login_required
def export_to_excel(request, queryset=None, filename="export.xlsx"):
    """
    Reusable export function that can be called:
    1. As a Django view (Django passes request, queryset=None).
    2. As a helper by passing your own queryset explicitly.
    """
    doc_type = "all"
    date_from = request.GET.get("date_from", "")
    date_to = request.GET.get("date_to", "")
    user = request.user

    if queryset is None:
        # Detect doc_type
        doc_type = request.GET.get("doc_type", "all")
        if doc_type == "all" and "HTTP_REFERER" in request.META:
            referer_path = request.META["HTTP_REFERER"]
            if "sales-promotion" in referer_path:
                doc_type = "sales_promos"
            elif "personal-data-sheet" in referer_path:
                doc_type = "personal_data_sheets"
            elif "service-repair" in referer_path:
                doc_type = "service_accreditations"
            elif "inspection-validation" in referer_path:
                doc_type = "inspection_reports"
            elif "order-of-payment" in referer_path:
                doc_type = "orders_of_payment"
            elif "checklist-evaluation" in referer_path:
                doc_type = "checklist_evaluation_sheets"

        # Convert dates if passed explicitly
        date_from_obj = None
        date_to_obj = None
        if date_from:
            try:
                date_from_obj = datetime.datetime.strptime(date_from, "%Y-%m-%d").date()
            except ValueError:
                pass
        if date_to:
            try:
                date_to_obj = datetime.datetime.strptime(date_to, "%Y-%m-%d").date()
            except ValueError:
                pass

        def apply_filters(qs):
            search = request.GET.get("search", "")
            if search:
                qs = qs.filter(
                    Q(user__username__icontains=search) |
                    Q(id__icontains=search)
                )
            if date_from_obj:
                qs = qs.filter(Q(date_filed__gte=date_from_obj) | Q(date__gte=date_from_obj))
            if date_to_obj:
                qs = qs.filter(Q(date_filed__lte=date_to_obj) | Q(date__lte=date_to_obj))
            return qs

        if doc_type == "sales_promos":
            queryset = apply_filters(UserRoleMixin.get_queryset_or_all(SalesPromotionPermitApplication, user))
        elif doc_type == "personal_data_sheets":
            queryset = apply_filters(UserRoleMixin.get_queryset_or_all(PersonalDataSheet, user))
        elif doc_type == "service_accreditations":
            queryset = apply_filters(UserRoleMixin.get_queryset_or_all(ServiceRepairAccreditationApplication, user))
        elif doc_type == "inspection_reports":
            queryset = apply_filters(UserRoleMixin.get_queryset_or_all(InspectionValidationReport, user))
        elif doc_type == "orders_of_payment":
            queryset = apply_filters(UserRoleMixin.get_queryset_or_all(OrderOfPayment, user))
        elif doc_type == "checklist_evaluation_sheets":
            queryset = apply_filters(UserRoleMixin.get_queryset_or_all(ChecklistEvaluationSheet, user))
        else:
            queryset = chain(
                apply_filters(UserRoleMixin.get_queryset_or_all(SalesPromotionPermitApplication, user)),
                apply_filters(UserRoleMixin.get_queryset_or_all(PersonalDataSheet, user)),
                apply_filters(UserRoleMixin.get_queryset_or_all(ServiceRepairAccreditationApplication, user)),
                apply_filters(UserRoleMixin.get_queryset_or_all(InspectionValidationReport, user)),
                apply_filters(UserRoleMixin.get_queryset_or_all(OrderOfPayment, user)),
                apply_filters(UserRoleMixin.get_queryset_or_all(ChecklistEvaluationSheet, user)),
            )

    # --- Auto-detect min/max dates if not provided ---
    date_field_candidates = ["date_filed", "date"]  # common fields in your models
    min_date, max_date = None, None

    try:
        # Only works if queryset is a real QuerySet (not itertools.chain)
        if hasattr(queryset, "aggregate"):
            for field in date_field_candidates:
                if field in [f.name for f in queryset.model._meta.fields]:
                    agg = queryset.aggregate(
                        min_date=Min(field),
                        max_date=Max(field),
                    )
                    min_date, max_date = agg["min_date"], agg["max_date"]
                    if min_date or max_date:
                        break
    except Exception:
        # Fallback if queryset is a chain → iterate manually
        dates = []
        for doc in queryset:
            d = getattr(doc, "date_filed", None) or getattr(doc, "date", None)
            if d:
                dates.append(d)
        if dates:
            min_date, max_date = min(dates), max(dates)

    # --- Build descriptive filename ---
    date_part = ""
    if min_date and max_date:
        date_part = f"_{min_date.strftime('%Y-%m-%d')}_to_{max_date.strftime('%Y-%m-%d')}"
    filename = f"{doc_type}{date_part}.xlsx"

    # --- Build Excel ---
    wb = Workbook()
    ws = wb.active
    ws.title = "Export"
    ws.append(["Document Type", "ID", "Filed By", "Date Filed"])

    for doc in queryset:
        doc_type_name = doc._meta.verbose_name
        doc_id = getattr(doc, "id", "")
        filed_by = getattr(doc, "user", None)
        date_filed = getattr(doc, "date_filed", None) or getattr(doc, "date", "")
        ws.append([doc_type_name, str(doc_id), str(filed_by), str(date_filed)])

    # --- Response ---
    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    safe_filename = quote(filename)
    response["Content-Disposition"] = f"attachment; filename={safe_filename}; filename*=UTF-8''{safe_filename}"
    wb.save(response)
    return response