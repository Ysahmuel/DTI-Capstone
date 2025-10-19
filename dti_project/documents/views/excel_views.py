import datetime
from io import BytesIO
from itertools import chain
import json
import re
import threading
import time
from urllib.parse import quote
import uuid
from django.urls import reverse
from django.views import View
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill
from openpyxl.utils import get_column_letter
from django.http import HttpResponse, HttpResponseRedirect, StreamingHttpResponse
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
from django.http import JsonResponse
from django.core.cache import cache

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
    Returns immediately and lets the client poll for status.
    Processing happens synchronously but progress is tracked.
    """
    
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
        # Check if this is a status check request
        if request.POST.get('check_status'):
            session_id = request.POST.get('session_id')
            progress_data = cache.get(f'upload_progress_{session_id}')
            return JsonResponse(progress_data or {'status': 'not_found'})

        files = request.FILES.getlist("files")

        if not files:
            return JsonResponse({
                'status': 'error',
                'message': 'No files were uploaded.'
            })

        # Get or create session ID
        session_id = request.POST.get('session_id')
        if not session_id:
            session_id = str(uuid.uuid4())

        # Store files temporarily in cache (convert to byte strings)
        file_data_list = []
        for file in files:
            file_data_list.append({
                'name': file.name,
                'content': file.read(),
            })
        
        cache.set(f'upload_files_{session_id}', file_data_list, timeout=600)

        # Initialize progress
        self._update_progress(session_id, {
            'status': 'queued',
            'current_row': 0,
            'total_rows': 0,
            'current_file': 0,
            'total_files': len(files),
            'percentage': 0,
            'message': 'Upload queued...'
        })

        # Return session ID immediately
        return JsonResponse({
            'status': 'queued',
            'session_id': session_id
        })

    def _update_progress(self, session_id, data):
        """Update progress in cache with timestamp"""
        data['timestamp'] = time.time()
        cache_key = f'upload_progress_{session_id}'
        cache.set(cache_key, data, timeout=600)
        print(f"[PROGRESS] {cache_key}: {data}")  # Debug log


class ProcessUploadView(View):
    """
    Separate view that processes the upload.
    This is called via AJAX and streams progress updates.
    """
    
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
    
    def get(self, request, session_id):
        def process_and_stream():
            try:
                # Get files from cache
                file_data_list = cache.get(f'upload_files_{session_id}')
                if not file_data_list:
                    yield self._sse_message({'status': 'error', 'message': 'Files not found'})
                    return

                yield self._sse_message({
                    'status': 'processing',
                    'message': 'Starting processing...',
                    'percentage': 0
                })

                created_reports = []
                
                # First pass: Count total rows
                total_rows = 0
                file_row_counts = []
                
                yield self._sse_message({
                    'status': 'counting',
                    'message': 'Counting rows...',
                    'percentage': 0
                })
                
                for file_data in file_data_list:
                    ext = os.path.splitext(file_data['name'])[1].lower()
                    if file_data['name'].startswith("~$") or ext not in [".xlsx", ".xls"]:
                        file_row_counts.append(0)
                        continue
                    
                    try:
                        file_obj = BytesIO(file_data['content'])
                        wb = load_workbook(file_obj, data_only=True)
                        ws = wb.active
                        row_count = max(0, ws.max_row - 2)
                        file_row_counts.append(row_count)
                        total_rows += row_count
                        wb.close()
                    except Exception as e:
                        print(f"Error counting rows: {e}")
                        file_row_counts.append(0)

                yield self._sse_message({
                    'status': 'processing',
                    'current_row': 0,
                    'total_rows': total_rows,
                    'current_file': 0,
                    'total_files': len(file_data_list),
                    'percentage': 0,
                    'message': f'Processing {total_rows} rows...'
                })

                # Create ONE report for all files
                report = CollectionReport.objects.create()
                created_reports.append(report)
                
                # Track metadata extracted from files
                date_from = None
                date_to = None
                certification_text = None
                collecting_officer_name = None
                special_collecting_officer = None
                special_collecting_officer_date = None
                official_designation = None
                undeposited_collections = None
                total_collections = None
                
                # Update cache with created reports for cancellation
                cache.set(f'upload_reports_{session_id}', [report.pk], timeout=600)

                current_row = 0
                
                # Process each file
                for file_index, file_data in enumerate(file_data_list):
                    ext = os.path.splitext(file_data['name'])[1].lower()
                    
                    yield self._sse_message({
                        'status': 'processing',
                        'current_row': current_row,
                        'total_rows': total_rows,
                        'current_file': file_index + 1,
                        'total_files': len(file_data_list),
                        'percentage': round((current_row / total_rows * 100) if total_rows > 0 else 0, 2),
                        'message': f'Processing {file_data["name"]}...',
                        'current_filename': file_data['name']
                    })
                    
                    if file_data['name'].startswith("~$") or ext not in [".xlsx", ".xls"]:
                        continue

                    try:
                        file_obj = BytesIO(file_data['content'])
                        wb = load_workbook(file_obj, data_only=True)
                        ws = wb.active
                    except Exception as e:
                        print(f"Error opening file: {e}")
                        continue

                    # === Extract metadata from first file only ===
                    if file_index == 0:
                        try:
                            # Extract Date From, Date To, Summary, and Certification data
                            for row_idx in range(1, min(ws.max_row + 1, 100)):  # Check up to 100 rows
                                row = ws[row_idx]
                                
                                # Check all cells in the row for labels (horizontal layout)
                                for col_idx in range(len(row) - 1):  # -1 because we need col+1 for value
                                    cell_label = str(row[col_idx].value).strip().lower() if row[col_idx].value else ""
                                    cell_value = row[col_idx + 1].value if col_idx + 1 < len(row) else None
                                    
                                    # Extract Date From (horizontal: label in col, value in col+1)
                                    if "date from" in cell_label and cell_value:
                                        if isinstance(cell_value, datetime.datetime):
                                            date_from = cell_value.date()
                                        elif isinstance(cell_value, datetime.date):
                                            date_from = cell_value
                                        elif isinstance(cell_value, (int, float)):
                                            try:
                                                base_date = datetime.datetime(1899, 12, 30)
                                                date_from = (base_date + datetime.timedelta(days=float(cell_value))).date()
                                            except:
                                                pass
                                        elif isinstance(cell_value, str):
                                            # Try multiple date formats
                                            for date_format in ["%m/%d/%Y", "%Y-%m-%d", "%d-%b-%y", "%d/%m/%Y"]:
                                                try:
                                                    date_from = datetime.datetime.strptime(cell_value.strip(), date_format).date()
                                                    break
                                                except:
                                                    pass
                                    
                                    # Extract Date To (horizontal: label in col, value in col+1)
                                    elif "date to" in cell_label and cell_value:
                                        if isinstance(cell_value, datetime.datetime):
                                            date_to = cell_value.date()
                                        elif isinstance(cell_value, datetime.date):
                                            date_to = cell_value
                                        elif isinstance(cell_value, (int, float)):
                                            try:
                                                base_date = datetime.datetime(1899, 12, 30)
                                                date_to = (base_date + datetime.timedelta(days=float(cell_value))).date()
                                            except:
                                                pass
                                        elif isinstance(cell_value, str):
                                            # Try multiple date formats
                                            for date_format in ["%m/%d/%Y", "%Y-%m-%d", "%d-%b-%y", "%d/%m/%Y"]:
                                                try:
                                                    date_to = datetime.datetime.strptime(cell_value.strip(), date_format).date()
                                                    break
                                                except:
                                                    pass
                                    
                                    # Extract Undeposited Collections
                                    elif "undeposited collections per last report" in cell_label:
                                        # Check a few columns to the right for the value
                                        for offset in range(1, 10):
                                            if col_idx + offset < len(row) and row[col_idx + offset].value:
                                                try:
                                                    undeposited_collections = float(str(row[col_idx + offset].value).replace(',', ''))
                                                    break
                                                except:
                                                    pass
                                    
                                    # Extract Total Collections
                                    elif cell_label == "total" or (cell_label.startswith("total") and "undeposited" not in cell_label):
                                        # Check a few columns to the right for the value
                                        for offset in range(1, 10):
                                            if col_idx + offset < len(row) and row[col_idx + offset].value:
                                                try:
                                                    val = float(str(row[col_idx + offset].value).replace(',', ''))
                                                    # Only set if it's a reasonable number (not 0)
                                                    if val > 0:
                                                        total_collections = val
                                                        break
                                                except:
                                                    pass
                                    
                                    # Extract Certification Text
                                    if "certification" in cell_label:
                                        # Look for the certification paragraph in the next few rows
                                        cert_lines = []
                                        for cert_row_idx in range(row_idx + 1, min(row_idx + 10, ws.max_row + 1)):
                                            cert_row = ws[cert_row_idx]
                                            # Check first few columns for text
                                            for cert_col in range(min(5, len(cert_row))):
                                                if cert_row[cert_col].value:
                                                    cert_text = str(cert_row[cert_col].value).strip()
                                                    if cert_text and len(cert_text) > 20:  # Likely paragraph text
                                                        cert_lines.append(cert_text)
                                                        break
                                            # Stop if we hit "Name and Signature"
                                            if any(cert_row[i].value and "name and signature" in str(cert_row[i].value).lower() 
                                                   for i in range(min(5, len(cert_row)))):
                                                break
                                        if cert_lines:
                                            certification_text = " ".join(cert_lines[:3])  # Take first 3 lines
                                    
                                    # Extract Name and Signature of Collecting Officer
                                    elif "name and signature of collecting officer" in cell_label:
                                        # Look above this row for the name in nearby columns
                                        if row_idx > 0:
                                            name_row = ws[row_idx - 1]
                                            for offset in range(min(10, len(name_row))):
                                                if name_row[offset].value:
                                                    name_val = str(name_row[offset].value).strip()
                                                    if name_val and len(name_val) > 3:  # Likely a name
                                                        collecting_officer_name = name_val
                                                        break
                                    
                                    # Extract Special Collecting Officer
                                    elif "special collecting officer" in cell_label:
                                        # Look for value in next columns
                                        for offset in range(1, 5):
                                            if col_idx + offset < len(row) and row[col_idx + offset].value:
                                                val = str(row[col_idx + offset].value).strip()
                                                # Check if it's a name (not a date)
                                                if val and len(val) > 3 and not any(char.isdigit() for char in val[:3]):
                                                    special_collecting_officer = val
                                                    break
                                        
                                        # Check next columns for date
                                        for offset in range(1, 8):
                                            if col_idx + offset < len(row) and row[col_idx + offset].value:
                                                date_val = row[col_idx + offset].value
                                                if isinstance(date_val, datetime.datetime):
                                                    special_collecting_officer_date = date_val.date()
                                                    break
                                                elif isinstance(date_val, datetime.date):
                                                    special_collecting_officer_date = date_val
                                                    break
                                                elif isinstance(date_val, str):
                                                    for date_format in ["%d-%b-%y", "%m/%d/%Y", "%Y-%m-%d"]:
                                                        try:
                                                            special_collecting_officer_date = datetime.datetime.strptime(date_val.strip(), date_format).date()
                                                            break
                                                        except:
                                                            pass
                                                    if special_collecting_officer_date:
                                                        break
                                    
                                    # Extract Official Designation
                                    elif "official designation" in cell_label:
                                        # Look for value in next columns
                                        for offset in range(1, 5):
                                            if col_idx + offset < len(row) and row[col_idx + offset].value:
                                                official_designation = str(row[col_idx + offset].value).strip()
                                                break
                                            
                        except Exception as e:
                            print(f"Error extracting metadata: {e}")
                            import traceback
                            traceback.print_exc()

                    # Auto-detect header row with more flexibility
                    header_row = None
                    for i, row in enumerate(ws.iter_rows(values_only=True), start=1):
                        cells = [str(c).strip().lower() if c else "" for c in row]
                        # Look for key indicators of header row
                        header_keywords = [
                            "official receipt", "receipt number", "number", "or number",
                            "date", "payor", "particulars", "amount", "rc code"
                        ]
                        matches = sum(1 for keyword in header_keywords if any(keyword in cell for cell in cells))
                        
                        # If we find at least 3 header keywords, likely a header row
                        if matches >= 3:
                            header_row = i
                            break

                    if not header_row:
                        print(f"Could not find header row in {file_data['name']}")
                        wb.close()
                        continue

                    # Check if next row is a sub-header (common in government forms)
                    has_subheader = False
                    if header_row < ws.max_row:
                        next_row = list(ws[header_row + 1])
                        next_values = [str(cell.value).strip().lower() if cell.value else "" for cell in next_row]
                        # Sub-headers usually have short text
                        if any(val and len(val) < 20 and val not in ['', 'none'] for val in next_values):
                            has_subheader = True

                    # Build headers - combine main header with sub-header if exists
                    headers = []
                    main_header_row = ws[header_row]
                    
                    if has_subheader:
                        sub_header_row = ws[header_row + 1]
                        for c1, c2 in zip(main_header_row, sub_header_row):
                            part1 = str(c1.value).strip() if c1.value else ""
                            part2 = str(c2.value).strip() if c2.value else ""
                            combined = f"{part1} {part2}".strip()
                            headers.append(self.normalize_header(combined) if combined else "")
                    else:
                        for cell in main_header_row:
                            val = str(cell.value).strip() if cell.value else ""
                            headers.append(self.normalize_header(val) if val else "")

                    print(f"Detected headers in {file_data['name']}: {headers}")  # Debug

                    # Smart field mapping with multiple possible matches
                    field_map = {}
                    
                    # Define possible header names for each field
                    field_aliases = {
                        'number': ['number', 'official_receipt_number', 'or_number', 'receipt_number', 'or_no', 'receipt_no'],
                        'date': ['date'],
                        'payor': ['payor', 'payer', 'name'],
                        'particulars': ['particulars', 'particular', 'description', 'purpose'],
                        'amount': ['amount', 'total', 'total_amount'],
                        'deposit': ['deposit', 'deposits'],
                    }
                    
                    # Try to map each field
                    for field_name, possible_headers in field_aliases.items():
                        if field_name not in field_map:
                            for idx, header in enumerate(headers):
                                if not header:
                                    continue
                                # Check if this header matches any of the possible names
                                if any(possible in header for possible in possible_headers):
                                    field_map[header] = field_name
                                    print(f"Mapped '{header}' -> '{field_name}'")  # Debug
                                    break
                    
                    # Also try automatic mapping from model fields
                    for f in CollectionReportItem._meta.fields:
                        normalized_field_name = self.normalize_header(f.verbose_name or f.name)
                        for idx, header in enumerate(headers):
                            if header and header not in field_map and normalized_field_name in header:
                                field_map[header] = f.name
                                print(f"Auto-mapped '{header}' -> '{f.name}'")  # Debug

                    print(f"Final field mapping: {field_map}")  # Debug
                    
                    if not field_map:
                        print(f"No field mappings found for {file_data['name']}")
                        wb.close()
                        continue

                    # Use the single report created earlier
                    db_column_indices = [idx for idx, h in enumerate(headers) if h and h in field_map]
                    empty_row_count = 0
                    MAX_EMPTY_ROWS = 5
                    
                    # Determine starting row (skip sub-header if present)
                    start_row = header_row + 2 if has_subheader else header_row + 1

                    # Process rows
                    for row_index, row in enumerate(ws.iter_rows(min_row=start_row, values_only=True), start=start_row):
                        if not any(row[idx] if idx < len(row) else None for idx in db_column_indices):
                            empty_row_count += 1
                            if empty_row_count >= MAX_EMPTY_ROWS:
                                break
                            continue

                        empty_row_count = 0
                        current_row += 1
                        
                        # Send update every 5 rows for better performance
                        if current_row % 5 == 0:
                            percentage = round((current_row / total_rows * 100) if total_rows > 0 else 0, 2)
                            yield self._sse_message({
                                'status': 'processing',
                                'current_row': current_row,
                                'total_rows': total_rows,
                                'current_file': file_index + 1,
                                'total_files': len(file_data_list),
                                'percentage': percentage,
                                'message': f'Processing row {current_row} of {total_rows}',
                                'current_filename': file_data['name']
                            })

                        data = {}
                        for idx, value in enumerate(row):
                            header = headers[idx] if idx < len(headers) else None
                            field_name = field_map.get(header)
                            if not field_name:
                                continue

                            # Handle Date column
                            if field_name == "date":
                                if isinstance(value, datetime.datetime):
                                    value = value.date()
                                elif isinstance(value, float):
                                    base_date = datetime.datetime(1899, 12, 30)
                                    value = base_date + datetime.timedelta(days=value)
                                    value = value.date()
                                elif isinstance(value, str):
                                    try:
                                        value = datetime.datetime.strptime(value.strip(), "%Y-%m-%d").date()
                                    except:
                                        try:
                                            value = datetime.datetime.strptime(value.strip(), "%m/%d/%Y").date()
                                        except:
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

                    wb.close()

                # Update report with all extracted metadata
                update_fields = []
                
                if date_from:
                    report.date_from = date_from
                    update_fields.append('date_from')
                if date_to:
                    report.date_to = date_to
                    update_fields.append('date_to')
                if certification_text:
                    report.certification_text = certification_text
                    update_fields.append('certification_text')
                if collecting_officer_name:
                    report.collecting_officer_name = collecting_officer_name
                    update_fields.append('collecting_officer_name')
                if special_collecting_officer:
                    report.special_collecting_officer = special_collecting_officer
                    update_fields.append('special_collecting_officer')
                if special_collecting_officer_date:
                    report.special_collecting_officer_date = special_collecting_officer_date
                    update_fields.append('special_collecting_officer_date')
                if official_designation:
                    report.official_designation = official_designation
                    update_fields.append('official_designation')
                if undeposited_collections:
                    report.undeposited_collections = undeposited_collections
                    update_fields.append('undeposited_collections')
                if total_collections:
                    report.total_collections = total_collections
                    update_fields.append('total_collections')
                
                if update_fields:
                    report.save(update_fields=update_fields)

                # Send final completion message
                redirect_url = reverse("collection-report", args=[report.pk])
                
                yield self._sse_message({
                    'status': 'complete',
                    'current_row': total_rows,
                    'total_rows': total_rows,
                    'current_file': len(file_data_list),
                    'total_files': len(file_data_list),
                    'percentage': 100,
                    'message': 'Upload complete!',
                    'redirect_url': redirect_url
                })

                # Clean up cache
                cache.delete(f'upload_files_{session_id}')

            except Exception as e:
                print(f"Processing error: {e}")
                import traceback
                traceback.print_exc()
                yield self._sse_message({
                    'status': 'error',
                    'message': f'Error: {str(e)}'
                })
        
        response = StreamingHttpResponse(
            process_and_stream(),
            content_type='text/event-stream'
        )
        response['Cache-Control'] = 'no-cache'
        response['X-Accel-Buffering'] = 'no'
        return response
    
    def _handle_cancellation(self, session_id, created_reports):
        """Handle cancellation with progress feedback"""
        total_reports = len(created_reports)
        
        yield self._sse_message({
            'status': 'cancelling',
            'message': 'Cancelling upload...',
            'percentage': 0
        })
        
        for idx, report in enumerate(created_reports):
            # Get item count before deletion
            item_count = report.report_items.count()
            
            # Delete report and its items
            report.report_items.all().delete()
            report.delete()
            
            percentage = round(((idx + 1) / total_reports * 100) if total_reports > 0 else 100, 2)
            
            yield self._sse_message({
                'status': 'cancelling',
                'message': f'Deleted report {idx + 1} of {total_reports} ({item_count} items)',
                'percentage': percentage,
                'current_report': idx + 1,
                'total_reports': total_reports
            })
        
        # Clean up cache
        cache.delete(f'upload_files_{session_id}')
        cache.delete(f'upload_reports_{session_id}')
        cache.delete(f'upload_cancel_{session_id}')
        
        yield self._sse_message({
            'status': 'cancelled',
            'message': 'Upload cancelled successfully',
            'percentage': 100
        })
    
    def _sse_message(self, data):
        """Format data as SSE message"""
        return f"data: {json.dumps(data)}\n\n"


class UploadProgressStreamView(View):
    """Legacy view - kept for backwards compatibility but not used in new flow"""
    
    def get(self, request, session_id):
        progress_data = cache.get(f'upload_progress_{session_id}')
        return JsonResponse(progress_data or {'status': 'not_found'})
    
class CancelUploadView(View):
    """Cancel an ongoing upload"""
    
    def post(self, request, session_id):
        # Set cancellation flag
        cache.set(f'upload_cancel_{session_id}', True, timeout=600)
        return JsonResponse({'status': 'cancellation_requested'})