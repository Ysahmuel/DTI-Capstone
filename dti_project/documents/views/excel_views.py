import datetime
from itertools import chain
from urllib.parse import quote
from django.urls import reverse
from django.views import View
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill
from openpyxl.utils import get_column_letter
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.apps import apps
from ..utils.excel_view_helpers import normalize_sheet_name, to_title
from ..models.base_models import DraftModel
from django.contrib.auth.mixins import LoginRequiredMixin
from ..mixins.permissions_mixins import UserRoleMixin
from django.shortcuts import render
from django.contrib import messages
from django.db import transaction
import pandas as pd
from openpyxl import load_workbook

import os
from ..models import (
    ChecklistEvaluationSheet,
    InspectionValidationReport,
    OrderOfPayment,
    PersonalDataSheet,
    SalesPromotionPermitApplication,
    ServiceRepairAccreditationApplication,
)

MODEL_MAP = {
    model._meta.model_name: model
    for model in apps.get_models()
    if issubclass(model, DraftModel) and not model._meta.abstract
}

EXPORT_MODEL_MAP = {
    "salespromotionpermitapplication": SalesPromotionPermitApplication,
    "personaldatasheet": PersonalDataSheet,
    "servicerepairaccreditationapplication": ServiceRepairAccreditationApplication,
    "inspectionvalidationreport": InspectionValidationReport,
    "orderofpayment": OrderOfPayment,
    "checklistevaluationsheet": ChecklistEvaluationSheet,
}

class ExportDocumentsExcelView(LoginRequiredMixin, View):
    """
    Export selected documents (via checkboxes) or all filtered documents to Excel.
    Preserves grouped formatting, headers, styling, and filename date ranges.
    """

    def post(self, request, *args, **kwargs):
        user = request.user
        selected_docs = request.POST.getlist("documents")

        # --- Collect documents by model ---
        grouped = {}
        if selected_docs:
            # Use checkbox selection
            grouped_ids = {}
            for doc in selected_docs:
                try:
                    model_name, pk = doc.split(":")
                    grouped_ids.setdefault(model_name.lower(), []).append(pk)
                except ValueError:
                    continue

            for model_name, ids in grouped_ids.items():
                model = EXPORT_MODEL_MAP.get(model_name)
                if not model:
                    continue
                qs = UserRoleMixin.get_queryset_or_all(model, user).filter(pk__in=ids)
                if qs.exists():
                    grouped[model._meta.verbose_name_plural.title()] = list(qs)
        else:
            # If no checkboxes, export all (apply UserRoleMixin)
            for model in EXPORT_MODEL_MAP.values():
                qs = UserRoleMixin.get_queryset_or_all(model, user)
                if qs.exists():
                    grouped[model._meta.verbose_name_plural.title()] = list(qs)

        # --- Create workbook ---
        wb = Workbook()
        wb.remove(wb.active)

        for model_name, objs in grouped.items():
            if not objs:
                continue
            ws = wb.create_sheet(title=model_name[:31])
            fields = objs[0]._meta.fields
            headers = [f.verbose_name.title() for f in fields]
            ws.append(headers)

            # Style headers
            for col_num, header in enumerate(headers, 1):
                cell = ws.cell(row=1, column=col_num)
                cell.font = Font(bold=True)
                cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
                cell.fill = PatternFill(start_color="DDDDDD", end_color="DDDDDD", fill_type="solid")

            # Rows
            for obj in objs:
                row = []
                for f in fields:
                    val = getattr(obj, f.name, "")
                    if isinstance(val, datetime.datetime):
                        val = val.date()
                    if val is None:
                        val = ""
                    row.append(to_title(str(val)))
                ws.append(row)

            # Auto-size columns
            for col_num, col_cells in enumerate(ws.columns, 1):
                max_length = 0
                column = get_column_letter(col_num)
                for cell in col_cells:
                    if cell.value:
                        max_length = max(max_length, len(str(cell.value)))
                ws.column_dimensions[column].width = min(max_length + 2, 50)

            # Freeze header
            ws.freeze_panes = "A2"

        # --- Filename with date range ---
        dates = []
        for objs in grouped.values():
            for doc in objs:
                d = getattr(doc, "date_filed", None) or getattr(doc, "date", None)
                if d:
                    if isinstance(d, datetime.datetime):
                        d = d.date()
                    dates.append(d)
        min_date, max_date = (min(dates), max(dates)) if dates else (None, None)
        date_part = f"{min_date}_{max_date}" if min_date and max_date else ""

        filename = f"Documents_{date_part}.xlsx" if date_part else "Documents.xlsx"

        response = HttpResponse(
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        safe_filename = quote(filename)
        response["Content-Disposition"] = f"attachment; filename={safe_filename}; filename*=UTF-8''{safe_filename}"
        wb.save(response)
        return response


class UploadExcelView(LoginRequiredMixin, View):
    """
    Upload an Excel file and import rows into Django models.
    Only allows .xlsx/.xls files.
    """

    template_name = "documents/excel_templates/excel_upload.html"

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        file = request.FILES.get("file")
        if not file:
            messages.error(request, "No file uploaded.")
            return HttpResponseRedirect(reverse("documents:upload_excel"))

        # --- Validate if file extension is xlsx (excel file) ---
        ext = os.path.splitext(file.name)[1].lower()
        if ext not in [".xlsx", ".xls"]:
            messages.error(request, "Invalid file type. Please upload an Excel file (.xlsx or .xls).")
            return HttpResponseRedirect(reverse("documents:upload_excel"))

        try:
            wb = load_workbook(file)
        except Exception as e:
            messages.error(request, f"Invalid Excel file: {e}")
            return HttpResponseRedirect(reverse("documents:upload_excel"))

        imported_count = 0
        skipped_count = 0

        for sheetname in wb.sheetnames:
            model = EXPORT_MODEL_MAP.get(normalize_sheet_name(sheetname))
            if not model:
                continue

            ws = wb[sheetname]
            headers = [str(cell.value).strip().lower() for cell in ws[1]]

            for row in ws.iter_rows(min_row=2, values_only=True):
                if not any(row):
                    continue

                data = {}
                for header, value in zip(headers, row):
                    if not header:
                        continue

                    field = next(
                        (f for f in model._meta.fields if f.verbose_name.lower() == header),
                        None,
                    )
                    if not field:
                        continue

                    if isinstance(value, datetime.datetime):
                        value = value.date()
                    if value in ("", None):
                        value = None

                    data[field.name] = value

                try:
                    obj = model(**data)
                    obj.save()
                    imported_count += 1
                except Exception:
                    skipped_count += 1
                    continue

        messages.success(
            request,
            f"Imported {imported_count} records. Skipped {skipped_count} invalid rows."
        )
        return HttpResponseRedirect(reverse("documents:upload_excel"))