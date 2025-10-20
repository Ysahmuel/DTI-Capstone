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
    Initial upload endpoint - stores files in cache and returns session ID
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
        cache.set(f'upload_progress_{session_id}', {
            'status': 'queued',
            'current_row': 0,
            'total_rows': 0,
            'current_file': 0,
            'total_files': len(files),
            'percentage': 0,
            'message': 'Upload queued...',
            'timestamp': time.time()
        }, timeout=600)

        # Return session ID immediately
        return JsonResponse({
            'status': 'queued',
            'session_id': session_id
        })


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
        print(f"ProcessUploadView GET called with session_id: {session_id}")  # DEBUG     
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

                    # Auto-detect header row
                    header_row = None
                    for i, row in enumerate(ws.iter_rows(values_only=True), start=1):
                        cells = [str(c).strip().lower() for c in row if c]
                        if any("official receipt" in c or "date" == c for c in cells):
                            header_row = i
                            break

                    if not header_row:
                        wb.close()
                        continue

                    # Combine header rows
                    headers = []
                    for c1, c2 in zip(ws[header_row], ws[header_row + 1]):
                        part1 = str(c1.value).strip() if c1.value else ""
                        part2 = str(c2.value).strip() if c2.value else ""
                        combined = f"{part1} {part2}".strip()
                        headers.append(self.normalize_header(combined))

                    # Field mapping
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

                    # Process rows
                    for row_index, row in enumerate(ws.iter_rows(min_row=header_row + 2, values_only=True), start=header_row + 2):
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

                    created_reports.append(report)
                    wb.close()

                # Send final completion message
                redirect_url = reverse("collection-report", args=[created_reports[-1].pk]) if created_reports else reverse("all-documents")
                
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