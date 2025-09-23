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
from ..mappings import EXPORT_MODEL_MAP, UPLOAD_MODEL_MAP
from ..utils.excel_view_helpers import get_model_from_sheet, get_user_from_full_name, normalize_header, normalize_sheet_name, shorten_name, to_title
from django.contrib.auth.mixins import LoginRequiredMixin
from ..mixins.permissions_mixins import UserRoleMixin
from django.shortcuts import render
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
    """
    Upload one or more Excel files and import rows into Django models.
    """

    template_name = "documents/excel_templates/excel_upload.html"

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)

    def post(self, request, *args, **kwargs):
        files = request.FILES.getlist("files")

        if not files:
            messages.error(request, "No files were uploaded. Please select an Excel file to continue.")
            return HttpResponseRedirect(reverse("documents:all-documents"))

        total_imported = 0
        total_skipped = 0

        for file in files:
            ext = os.path.splitext(file.name)[1].lower()
            if ext not in [".xlsx", ".xls"]:
                messages.error(request, f"{file.name} was not uploaded. Only Excel files (.xlsx or .xls) are allowed.")
                continue

            try:
                wb = load_workbook(file)
            except Exception:
                messages.error(request, f"Could not open {file.name}. Please check that it is a valid Excel file.")
                continue

            for sheetname in wb.sheetnames:
                model = get_model_from_sheet(sheetname)
                if not model:
                    print(f"Skipping sheet: {sheetname} (no matching document type found)")
                    continue

                ws = wb[sheetname]
                raw_headers = [str(cell.value).strip() if cell.value else "" for cell in ws[1]]
                headers = [normalize_header(h) for h in raw_headers]

                # Build field mapping
                field_map = {}
                for f in model._meta.fields:
                    field_options = {
                        normalize_header(f.verbose_name),
                        normalize_header(f.name),
                    }
                    for h in headers:
                        if h in field_options:
                            field_map[h] = f.name

                print(f"Processing sheet: {sheetname}")
                print(f"   ↳ Matched model: {model.__name__}")
                print(f"   ↳ Headers: {headers}")
                print(f"   ↳ Field map: {field_map}")

                imported_count = 0
                skipped_count = 0

                for row in ws.iter_rows(min_row=2, values_only=True):
                    if not any(row):  # skip empty rows
                        continue

                    data = {}
                    for header, value in zip(headers, row):
                        field_name = field_map.get(header)
                        if not field_name:
                            continue

                        if isinstance(value, datetime.datetime):
                            value = value.date()
                        if value in ("", None):
                            value = None

                        # Special handling for user field
                        if field_name == "user" and value:
                            user_obj = get_user_from_full_name(str(value))
                            if user_obj:
                                data[field_name] = user_obj
                            else:
                                print(f"Could not find user: '{value}'. Row skipped.")
                                skipped_count += 1
                                data = {}
                                break
                        else:
                            data[field_name] = value

                    try:
                        if data:
                            with transaction.atomic():
                                obj = model(**data)
                                obj.save()
                                imported_count += 1
                        else:
                            skipped_count += 1

                    except IntegrityError as e:
                        print(f"Skipped row due to database error: {e}")
                        skipped_count += 1
                        continue
                    except Exception as e:
                        print(f"Skipped row due to error: {e}")
                        skipped_count += 1
                        continue

                total_imported += imported_count
                total_skipped += skipped_count

                print(f"Imported {imported_count} rows from {sheetname}, skipped {skipped_count}")

        # --- User-friendly messages ---
        if total_imported > 0:
            messages.success(request, f"Successfully imported {total_imported} records.")

        if total_skipped > 0:
            messages.error(
                request,
                f"{total_skipped} rows were skipped because of missing or invalid information. "
                "Please review your Excel file and try again."
            )

        if total_imported == 0 and total_skipped == 0:
            messages.info(
                request,
                "No records were imported. Please make sure your Excel sheets match the expected format."
            )

        return HttpResponseRedirect(reverse("all-documents"))