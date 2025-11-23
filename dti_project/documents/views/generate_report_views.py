import datetime
from itertools import chain
import re
from urllib.parse import quote
from django.views import View
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill
from openpyxl.utils import get_column_letter
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.apps import apps
from ..mixins.filter_mixins import FilterableDocumentMixin
from documents.utils.excel_view_helpers import shorten_name
from ..models.base_models import DraftModel
from django.contrib.auth.mixins import LoginRequiredMixin
from ..mixins.permissions_mixins import UserRoleMixin
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

def to_title(value):
    """Normalize strings: remove underscores, title-case, handle non-strings gracefully."""
    if not isinstance(value, str):
        return value
    return value.replace("_", " ").title()

def clean_sheet_name(name: str) -> str:
    """
    Format sheet name with spaces, title case, and Excel-safe rules.
    """
    # Normalize underscores and multiple spaces
    name = re.sub(r'[_\s]+', ' ', name)

    # Remove forbidden Excel characters
    name = re.sub(r'[:\\/?*\[\]]', '', name)

    # Title case
    name = to_title(name.strip())

    # Excel max length = 31 chars
    return name[:31]

class GenerateDocumentsReportView(LoginRequiredMixin, FilterableDocumentMixin, View):
    """
    Export filtered documents to Excel.
    Each document type gets its own sheet.
    """

    def post(self, request, *args, **kwargs):
        from openpyxl.utils import get_column_letter
        from openpyxl.styles import Border, Side
        
        # Fetch all draft models
        MODEL_MAP = {
            model._meta.model_name: model
            for model in apps.get_models()
            if issubclass(model, DraftModel) and not model._meta.abstract
        }

        wb = Workbook()
        wb.remove(wb.active)

        included_models = []
        all_summary_data = []
        all_statuses = set()

        for model_name, model in MODEL_MAP.items():
            qs = model.objects.all()
            filtered_qs = self.apply_filters(qs)
            objs = list(filtered_qs)

            if not objs:
                continue

            # Store the readable name for filename logic
            model_verbose_name = model._meta.verbose_name
            included_models.append(model_verbose_name)

            # Collect summary data
            status_counts = {}
            if hasattr(model, 'status'):
                for obj in objs:
                    status = str(getattr(obj, 'status', 'Unknown'))
                    status_counts[status] = status_counts.get(status, 0) + 1
                    all_statuses.add(status)
            
            all_summary_data.append({
                'document_type': to_title(model_verbose_name),
                'total_count': len(objs),
                'status_counts': status_counts
            })

            # Clean sheet name from verbose_name
            sheet_title = clean_sheet_name(model_verbose_name)
            ws = wb.create_sheet(title=sheet_title)

            # Prepare headers first to know column count (excluding 'id' field)
            fields = [f for f in model._meta.get_fields() 
                     if f.concrete and not f.many_to_many and f.name != 'id']
            headers = [to_title(f.verbose_name) for f in fields]
            num_cols = len(headers)

            # Create header section spanning F1:I1
            # Row 1: Title
            doc_type = to_title(model_verbose_name)
            ws.merge_cells('F1:I1')
            title_cell = ws['F1']
            title_cell.value = f"{doc_type} Report"
            title_cell.font = Font(name='Arial', bold=True, size=12)
            title_cell.alignment = Alignment(horizontal="center", vertical="center")
            ws.row_dimensions[1].height = 25
            
            # Row 2: Office Name
            ws.merge_cells('F2:I2')
            office_cell = ws['F2']
            office_cell.value = "DTI Albay Provincial Office"
            office_cell.font = Font(name='Arial', bold=True, size=10)
            office_cell.alignment = Alignment(horizontal="center", vertical="center")
            ws.row_dimensions[2].height = 20
            
            # Row 3: Date
            ws.merge_cells('F3:I3')
            date_cell = ws['F3']
            date_str = datetime.date.today().strftime("%B %d, %Y")
            date_cell.value = date_str
            date_cell.font = Font(name='Arial', size=10)
            date_cell.alignment = Alignment(horizontal="center", vertical="center")
            ws.row_dimensions[3].height = 20
            
            # Row 4: Empty row for spacing
            ws.row_dimensions[4].height = 10

            # Define border styles
            thick_border = Border(
                bottom=Side(style='thick', color='000000')
            )

            # Add bottom border to row 4 (separation line)
            for col_num in range(1, num_cols + 1):
                cell = ws.cell(row=4, column=col_num)
                cell.border = thick_border

            # Add headers at row 5
            for col_num, header in enumerate(headers, 1):
                cell = ws.cell(row=5, column=col_num)
                cell.value = header
                cell.font = Font(name='Arial', bold=True, size=10)
                cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
                # Add border to header cells (no gray background)
                cell.border = Border(
                    top=Side(style='thin', color='000000'),
                    bottom=Side(style='thin', color='000000'),
                    left=Side(style='thin', color='000000'),
                    right=Side(style='thin', color='000000')
                )
            
            # Set header row height
            ws.row_dimensions[5].height = 30

            # Add data rows (starting at row 6)
            current_row = 6
            for obj in objs:
                row = []
                for f in fields:
                    val = getattr(obj, f.name, "")
                    
                    # Handle datetime conversion
                    if isinstance(val, datetime.datetime):
                        val = val.date()
                    
                    # Handle None values
                    if val is None:
                        val = ""
                    
                    row.append(to_title(str(val)) if val != "" else "")
                
                for col_num, value in enumerate(row, 1):
                    cell = ws.cell(row=current_row, column=col_num)
                    cell.value = value
                    cell.font = Font(name='Arial', size=9)
                    cell.alignment = Alignment(horizontal="left", vertical="top", wrap_text=True)
                    # Add thin borders to data cells
                    cell.border = Border(
                        top=Side(style='thin', color='CCCCCC'),
                        bottom=Side(style='thin', color='CCCCCC'),
                        left=Side(style='thin', color='CCCCCC'),
                        right=Side(style='thin', color='CCCCCC')
                    )
                current_row += 1

            # Auto-adjust column widths
            for col_num in range(1, num_cols + 1):
                max_length = 0
                column_letter = get_column_letter(col_num)
                
                # Check headers and data rows
                for row_num in range(5, current_row):
                    cell = ws.cell(row=row_num, column=col_num)
                    if cell.value:
                        cell_length = len(str(cell.value))
                        max_length = max(max_length, cell_length)
                
                # Set width with reasonable limits
                adjusted_width = min(max(max_length + 2, 10), 50)
                ws.column_dimensions[column_letter].width = adjusted_width

        # Create Summary Sheet as the first sheet
        if all_summary_data:
            summary_ws = wb.create_sheet(title="Summary", index=0)
            
            # Sort statuses alphabetically for consistent columns
            sorted_statuses = sorted(list(all_statuses))
            
            # Calculate the end column for merging (C to C + num_columns - 1)
            num_status_cols = len(sorted_statuses)
            last_col_num = 2 + num_status_cols + 1  # C=3, + statuses + Total
            last_col_letter = get_column_letter(last_col_num)
            
            # Header section
            summary_ws.merge_cells(f'C1:{last_col_letter}1')
            title_cell = summary_ws['C1']
            title_cell.value = "Documents Summary Report"
            title_cell.font = Font(name='Arial', bold=True, size=14)
            title_cell.alignment = Alignment(horizontal="center", vertical="center")
            summary_ws.row_dimensions[1].height = 30
            
            # Office Name
            summary_ws.merge_cells(f'C2:{last_col_letter}2')
            office_cell = summary_ws['C2']
            office_cell.value = "DTI Albay Provincial Office"
            office_cell.font = Font(name='Arial', bold=True, size=11)
            office_cell.alignment = Alignment(horizontal="center", vertical="center")
            summary_ws.row_dimensions[2].height = 20
            
            # Date
            summary_ws.merge_cells(f'C3:{last_col_letter}3')
            date_cell = summary_ws['C3']
            date_cell.value = datetime.date.today().strftime("%B %d, %Y")
            date_cell.font = Font(name='Arial', size=10)
            date_cell.alignment = Alignment(horizontal="center", vertical="center")
            summary_ws.row_dimensions[3].height = 20
            
            # Spacing
            summary_ws.row_dimensions[4].height = 10
            
            # Separator
            for col_num in range(3, last_col_num + 1):
                col_letter = get_column_letter(col_num)
                summary_ws[f'{col_letter}4'].border = Border(bottom=Side(style='thick', color='000000'))
            
            # Define border style for table
            table_border = Border(
                top=Side(style='thin', color='000000'),
                bottom=Side(style='thin', color='000000'),
                left=Side(style='thin', color='000000'),
                right=Side(style='thin', color='000000')
            )
            
            # Summary table headers - Row 6
            current_row = 6
            col_index = 3  # Start at column C
            
            # Document Type header
            cell = summary_ws.cell(row=current_row, column=col_index)
            cell.value = "Document Type"
            cell.font = Font(name='Arial', bold=True, size=11)
            cell.alignment = Alignment(horizontal="center", vertical="center")
            cell.border = table_border
            col_index += 1
            
            # Status headers
            for status in sorted_statuses:
                cell = summary_ws.cell(row=current_row, column=col_index)
                cell.value = to_title(status)
                cell.font = Font(name='Arial', bold=True, size=11)
                cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
                cell.border = table_border
                col_index += 1
            
            # Total header
            cell = summary_ws.cell(row=current_row, column=col_index)
            cell.value = "Total"
            cell.font = Font(name='Arial', bold=True, size=11)
            cell.alignment = Alignment(horizontal="center", vertical="center")
            cell.border = table_border
            
            summary_ws.row_dimensions[current_row].height = 25
            
            # Add summary data rows
            current_row = 7
            status_totals = {status: 0 for status in sorted_statuses}
            total_all_documents = 0
            
            for data in all_summary_data:
                col_index = 3
                
                # Document Type
                cell = summary_ws.cell(row=current_row, column=col_index)
                cell.value = data['document_type']
                cell.font = Font(name='Arial', size=10)
                cell.border = table_border
                col_index += 1
                
                # Status counts
                for status in sorted_statuses:
                    count = data['status_counts'].get(status, 0)
                    cell = summary_ws.cell(row=current_row, column=col_index)
                    cell.value = count if count > 0 else ""
                    cell.font = Font(name='Arial', size=10)
                    cell.alignment = Alignment(horizontal="center", vertical="center")
                    cell.border = table_border
                    status_totals[status] += count
                    col_index += 1
                
                # Total for this document type
                cell = summary_ws.cell(row=current_row, column=col_index)
                cell.value = data['total_count']
                cell.font = Font(name='Arial', bold=True, size=10)
                cell.alignment = Alignment(horizontal="center", vertical="center")
                cell.border = table_border
                
                total_all_documents += data['total_count']
                current_row += 1
            
            # Add total row
            col_index = 3
            
            # "TOTAL" label
            cell = summary_ws.cell(row=current_row, column=col_index)
            cell.value = "TOTAL"
            cell.font = Font(name='Arial', bold=True, size=11)
            cell.border = table_border
            col_index += 1
            
            # Status totals
            for status in sorted_statuses:
                cell = summary_ws.cell(row=current_row, column=col_index)
                cell.value = status_totals[status]
                cell.font = Font(name='Arial', bold=True, size=11)
                cell.alignment = Alignment(horizontal="center", vertical="center")
                cell.border = table_border
                col_index += 1
            
            # Grand total
            cell = summary_ws.cell(row=current_row, column=col_index)
            cell.value = total_all_documents
            cell.font = Font(name='Arial', bold=True, size=11)
            cell.alignment = Alignment(horizontal="center", vertical="center")
            cell.border = table_border
            
            # Adjust column widths
            summary_ws.column_dimensions['C'].width = 35
            for col_num in range(4, last_col_num + 1):
                col_letter = get_column_letter(col_num)
                summary_ws.column_dimensions[col_letter].width = 15

        # Fallback sheet if nothing matched
        if not wb.sheetnames:
            ws = wb.create_sheet("No Data")
            ws['A1'] = "No Data Available"
            ws['A1'].font = Font(name='Arial', size=10)
            filename_prefix = "No Documents"
        else:
            if len(included_models) == 1:
                filename_prefix = to_title(included_models[0])
            else:
                filename_prefix = "All Documents"

        # Filename with date
        date_str = datetime.date.today().strftime("%Y-%m-%d")
        filename = f"{filename_prefix} Report {date_str}.xlsx"

        # Prepare downloadable response
        response = HttpResponse(
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        response["Content-Disposition"] = f'attachment; filename="{filename}"'
        wb.save(response)
        return response