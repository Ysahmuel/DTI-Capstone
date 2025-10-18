import datetime
from itertools import chain
import re
from urllib.parse import quote
from django.urls import reverse
from django.views import View
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill
from openpyxl.utils import get_column_letter
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from ..models.collection_models import CollectionReport, CollectionReportItem
from ..mappings import EXPORT_MODEL_MAP, UPLOAD_MODEL_MAP
from ..utils.excel_view_helpers import get_model_from_sheet, get_user_from_full_name, normalize_header, normalize_sheet_name, shorten_name, to_title
from django.contrib.auth.mixins import LoginRequiredMixin
from ..mixins.permissions_mixins import UserRoleMixin
from django.shortcuts import redirect, render
from django.contrib import messages
from django.db import IntegrityError, transaction
import pandas as pd
from openpyxl import load_workbook
from openpyxl.utils.datetime import from_excel
from django.utils.dateparse import parse_date

import os
from ..models import (
    ChecklistEvaluationSheet,
    InspectionValidationReport,
    OrderOfPayment,
    PersonalDataSheet,
    SalesPromotionPermitApplication,
    ServiceRepairAccreditationApplication,
)


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
            # use your helper instead of hard truncation
            sheet_title = shorten_name(model_name)
            ws = wb.create_sheet(title=sheet_title)

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
    
class UploadExcelView(View):
    @staticmethod
    def normalize_header(value):
        """Normalize headers to simplify matching."""
        return (
            str(value).strip()
            .lower()
            .replace(" ", "_")
            .replace("(", "")
            .replace(")", "")
            .replace("/", "_")
            .replace("-", "_")
        )

    def post(self, request, *args, **kwargs):
        files = request.FILES.getlist("files")

        if not files:
            messages.error(request, "No files were uploaded. Please select an Excel file to continue.")
            return redirect(reverse("documents:all-documents"))

        created_reports = []  # we'll store created reports to redirect to last one

        for file in files:
            ext = os.path.splitext(file.name)[1].lower()
            if file.name.startswith("~$") or ext not in [".xlsx", ".xls"]:
                messages.error(request, f"{file.name} was not uploaded. Invalid file.")
                continue

            try:
                wb = load_workbook(file, data_only=True)
                ws = wb.active
            except Exception:
                messages.error(request, f"Could not open {file.name}.")
                continue

            # === Auto-detect header row ===
            header_row = None
            for i, row in enumerate(ws.iter_rows(values_only=True), start=1):
                cells = [str(c).strip().lower() for c in row if c]
                if any("official receipt" in c or "date" == c for c in cells):
                    header_row = i
                    break

            if not header_row:
                messages.error(request, f"Header row not found in {file.name}.")
                continue

            # === Combine header + subheader row ===
            header_row_1 = header_row
            header_row_2 = header_row + 1
            headers = []
            for c1, c2 in zip(ws[header_row_1], ws[header_row_2]):
                part1 = str(c1.value).strip() if c1.value else ""
                part2 = str(c2.value).strip() if c2.value else ""
                combined = f"{part1} {part2}".strip()
                headers.append(self.normalize_header(combined))

            # === Field mapping ===
            field_map = {}
            for f in CollectionReportItem._meta.fields:
                opts = {self.normalize_header(f.verbose_name or ""), self.normalize_header(f.name)}
                for h in headers:
                    if h in opts:
                        field_map[h] = f.name

            # Manual mappings
            if "official_receipt_number" in headers:
                field_map["official_receipt_number"] = "number"
            if "official_receipt_number" not in field_map and "number" in headers:
                field_map["number"] = "number"
            if "date" not in field_map and any("date" in h for h in headers):
                date_header = next(h for h in headers if "date" in h)
                field_map[date_header] = "date"

            report = CollectionReport.objects.create()

            db_column_indices = [idx for idx, h in enumerate(headers) if h in field_map]
            empty_row_count = 0
            MAX_EMPTY_ROWS = 5

            for row_index, row in enumerate(ws.iter_rows(min_row=header_row + 2, values_only=True), start=header_row + 2):
                if not any(row[idx] for idx in db_column_indices):
                    empty_row_count += 1
                    if empty_row_count >= MAX_EMPTY_ROWS:
                        break
                    continue

                empty_row_count = 0
                data = {}

                for idx, value in enumerate(row):
                    header = headers[idx] if idx < len(headers) else None
                    field_name = field_map.get(header)
                    if not field_name:
                        continue

                    # ✅ Handle Date column properly
                    if field_name == "date":
                        if isinstance(value, datetime.datetime):
                            value = value.date()
                        elif isinstance(value, float):
                            # Excel serial date
                            base_date = datetime.datetime(1899, 12, 30)
                            value = base_date + datetime.timedelta(days=value)
                            value = value.date()
                        elif isinstance(value, str):
                            try:
                                value = datetime.datetime.strptime(value.strip(), "%Y-%m-%d").date()
                            except Exception:
                                try:
                                    value = datetime.datetime.strptime(value.strip(), "%m/%d/%Y").date()
                                except Exception:
                                    value = None

                    data[field_name] = value

                if not data:
                    continue

                try:
                    with transaction.atomic():
                        item = CollectionReportItem.objects.create(**data)
                        report.report_items.add(item)
                except Exception as e:
                    print(f"Failed to save row {row_index}: {e}")
                    continue

            created_reports.append(report)

        if created_reports:
            last_report = created_reports[-1]
            messages.success(request, "Excel file successfully uploaded.")
            return redirect(reverse("collection-report", args=[last_report.pk]))

        messages.error(request, "No valid reports were created.")
        return redirect(reverse("all-documents"))


class UploadReportView(View):
    template_name = "documents/excel_templates/upload_report.html"

    def get(self, request, *args, **kwargs):
        file_reports = request.session.get("file_reports", [])
        context = {"file_reports": file_reports}
        return render(request, self.template_name, context)
