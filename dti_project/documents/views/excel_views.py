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
from django.db.models import Q, Min, Max
from urllib.parse import quote

class ImportFromExcelView(View):
    pass


@login_required
def export_to_excel(request, queryset=None, filename="export.xlsx"):
    """
    Reusable export function that:
    1. Can be called as a Django view (request, queryset=None).
    2. Can be called as a helper with your own queryset.
    3. Dynamically groups rows by document type and exports all fields.
    """

    user = request.user
    doc_type = "all"
    date_from = request.GET.get("date_from", "")
    date_to = request.GET.get("date_to", "")

    # --- Detect doc_type ---
    if queryset is None:
        doc_type = request.GET.get("doc_type", "all")
        if doc_type == "all" and "HTTP_REFERER" in request.META:
            referer_path = request.META["HTTP_REFERER"]
            mapping = {
                "sales-promotion": "sales_promos",
                "personal-data-sheet": "personal_data_sheets",
                "service-repair": "service_accreditations",
                "inspection-validation": "inspection_reports",
                "order-of-payment": "orders_of_payment",
                "checklist-evaluation": "checklist_evaluation_sheets",
            }
            for key, value in mapping.items():
                if key in referer_path:
                    doc_type = value
                    break

        # --- Convert date strings ---
        date_from_obj, date_to_obj = None, None
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

        # --- Map doc_type to models ---
        model_map = {
            "sales_promos": SalesPromotionPermitApplication,
            "personal_data_sheets": PersonalDataSheet,
            "service_accreditations": ServiceRepairAccreditationApplication,
            "inspection_reports": InspectionValidationReport,
            "orders_of_payment": OrderOfPayment,
            "checklist_evaluation_sheets": ChecklistEvaluationSheet,
        }

        if doc_type in model_map:
            queryset = apply_filters(UserRoleMixin.get_queryset_or_all(model_map[doc_type], user))
        else:
            queryset = chain(*[
                apply_filters(UserRoleMixin.get_queryset_or_all(m, user))
                for m in model_map.values()
            ])

    # --- Group documents by model ---
    grouped = {}
    if hasattr(queryset, "__iter__") and not hasattr(queryset, "model"):
        for obj in queryset:
            model_name = obj._meta.verbose_name_plural.title()
            grouped.setdefault(model_name, []).append(obj)
    else:
        model_name = queryset.model._meta.verbose_name_plural.title()
        grouped[model_name] = list(queryset)

    # --- Create Excel workbook ---
    wb = Workbook()
    wb.remove(wb.active)  # remove default sheet

    for model_name, objs in grouped.items():
        if not objs:
            continue
        ws = wb.create_sheet(title=model_name[:31])  # Excel sheet name limit

        # Dynamic headers
        fields = objs[0]._meta.fields
        headers = [f.verbose_name.title() for f in fields]
        ws.append(headers)

        # Rows
        for obj in objs:
            row = []
            for f in fields:
                val = getattr(obj, f.name, "")
                if isinstance(val, datetime.datetime):
                    val = val.date()
                row.append(str(val) if val is not None else "")
            ws.append(row)

    # --- Calculate min/max dates for filename ---
    dates = []
    for objs in grouped.values():
        for doc in objs:
            d = getattr(doc, "date_filed", None) or getattr(doc, "date", None)
            if d:
                if isinstance(d, datetime.datetime):
                    d = d.date()
                dates.append(d)

    min_date, max_date = (min(dates), max(dates)) if dates else (None, None)

    # --- Build filename ---
    if min_date and max_date:
        date_part = f"{min_date.strftime('%Y-%m-%d')}_to_{max_date.strftime('%Y-%m-%d')}"
    else:
        date_part = ""

    if doc_type == "all":
        filename = f"All Documents from {date_part}.xlsx" if date_part else "All Documents.xlsx"
    else:
        filename = f"{doc_type}_{date_part}.xlsx" if date_part else f"{doc_type}.xlsx"

    # --- Build response ---
    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    safe_filename = quote(filename)
    response["Content-Disposition"] = f"attachment; filename={safe_filename}; filename*=UTF-8''{safe_filename}"
    wb.save(response)
    return response