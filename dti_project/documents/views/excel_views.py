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
from ..models.collection_models import CollectionReportItem
from ..mappings import EXPORT_MODEL_MAP, UPLOAD_MODEL_MAP
from ..utils.excel_view_helpers import get_model_from_sheet, get_user_from_full_name, normalize_header, normalize_sheet_name, shorten_name, to_title
from django.contrib.auth.mixins import LoginRequiredMixin
from ..mixins.permissions_mixins import UserRoleMixin
from django.shortcuts import redirect, render
from django.contrib import messages
from django.db import IntegrityError, transaction
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
            value.strip()
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

        file_reports = []

        for file in files:
            report = {
                "filename": file.name,
                "filesize": round(file.size / (1024 * 1024), 2),
                "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "total_records": 0,
                "imported_records": 0,
                "failed_records": 0,
                "documents": [],
            }

            ext = os.path.splitext(file.name)[1].lower()
            if file.name.startswith("~$"):
                messages.error(request, f"Temporary file {file.name} is not valid.")
                continue

            if ext not in [".xlsx", ".xls"]:
                messages.error(request, f"{file.name} was not uploaded. Only Excel files are allowed.")
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
                messages.error(request, f"Header row not found in {file.name}. Ensure it contains 'Official Receipt' or 'Date'.")
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

            # === Map headers to model fields ===
            field_map = {}
            for f in CollectionReportItem._meta.fields:
                opts = {self.normalize_header(f.verbose_name or ""), self.normalize_header(f.name)}
                for h in headers:
                    if h in opts:
                        field_map[h] = f.name

            # Map Official Receipt Number manually
            if "official_receipt_number" in headers:
                field_map["official_receipt_number"] = "number"

            # Ensure date header is mapped
            if "date" in headers and "date" not in field_map:
                field_map["date"] = "date"

            # Identify "No." column index to ignore
            no_column_index = 0
            for idx, header in enumerate(headers):
                normalized = header.lower().strip() if header else ""
                if 'no' in normalized and len(normalized) <= 5:
                    no_column_index = idx
                    break

            # DB column indices (for empty row check)
            db_column_indices = [idx for idx, header in enumerate(headers) if header in field_map]

            empty_row_count = 0
            MAX_EMPTY_ROWS = 5

            for row_index, row in enumerate(ws.iter_rows(min_row=header_row + 2, values_only=True), start=header_row + 2):
                meaningful_data_found = any(
                    row[idx] is not None and str(row[idx]).strip()
                    for idx in db_column_indices
                )

                if not meaningful_data_found:
                    empty_row_count += 1
                    if empty_row_count >= MAX_EMPTY_ROWS:
                        break  # HARD STOP after 5 consecutive empty rows
                    continue

                empty_row_count = 0  # reset counter

                # === Process row ===
                record = {
                    "display": "",
                    "model": "Collection Report Item",
                    "status": "Imported",
                    "invalid_fields": [],
                    "row_number": row_index
                }
                data = {}

                for idx, value in enumerate(row):
                    header = headers[idx]
                    field_name = field_map.get(header)
                    if not field_name:
                        continue  # Skip columns like "No."

                    # Convert dates and clean strings
                    if isinstance(value, datetime.datetime):
                        value = value.date()
                    elif isinstance(value, str):
                        value = value.strip()
                        if value == "":
                            value = None
                    elif isinstance(value, datetime.date):
                        pass  # already date
                    elif value is None:
                        value = None

                    data[field_name] = value

                if not data:
                    continue  # Skip rows with no mapped DB fields

                try:
                    with transaction.atomic():
                        obj = CollectionReportItem.objects.create(**data)
                        record["display"] = str(obj)
                        record["date_created"] = getattr(obj, "created_at", datetime.datetime.now()).strftime("%Y-%m-%d %H:%M:%S")
                    report["imported_records"] += 1
                except Exception as e:
                    record["status"] = "Failed"
                    record["display"] = f"Row {record['row_number']}"
                    field_match = re.search(r'NOT NULL constraint failed: \w+\.(\w+)', str(e).lower())
                    if field_match:
                        record["invalid_fields"].append(f"Missing required field ({field_match.group(1)})")
                    else:
                        record["invalid_fields"].append(str(e))
                    report["failed_records"] += 1

                # Increment total_records at report level
                report["total_records"] += 1

                record["invalid_fields_display"] = ", ".join(record["invalid_fields"]) if record["invalid_fields"] else "None"
                record["data"] = data  # <-- Attach data for template

                report["documents"].append(record)

            file_reports.append(report)

        request.session["file_reports"] = file_reports
        messages.success(request, "Excel upload processed successfully!")
        return redirect(reverse("upload-report"))


class UploadReportView(View):
    template_name = "documents/excel_templates/upload_report.html"

    def get(self, request, *args, **kwargs):
        file_reports = request.session.get("file_reports", [])
        context = {"file_reports": file_reports}
        return render(request, self.template_name, context)
