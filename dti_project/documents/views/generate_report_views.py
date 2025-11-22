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
        # Fetch all draft models
        MODEL_MAP = {
            model._meta.model_name: model
            for model in apps.get_models()
            if issubclass(model, DraftModel) and not model._meta.abstract
        }

        wb = Workbook()
        wb.remove(wb.active)

        included_models = []

        for model_name, model in MODEL_MAP.items():
            qs = model.objects.all()
            filtered_qs = self.apply_filters(qs)
            objs = list(filtered_qs)

            if not objs:
                continue

            # Store the readable name for filename logic
            model_verbose_name = model._meta.verbose_name
            included_models.append(model_verbose_name)

            # Clean sheet name from verbose_name
            sheet_title = clean_sheet_name(model_verbose_name)
            ws = wb.create_sheet(title=sheet_title)

            # Prepare headers
            fields = [f for f in model._meta.get_fields() if f.concrete and not f.many_to_many]
            headers = [to_title(f.verbose_name) for f in fields]
            ws.append(headers)

            # Format header row
            for col_num, header in enumerate(headers, 1):
                cell = ws.cell(row=1, column=col_num)
                cell.font = Font(bold=True)
                cell.alignment = Alignment(horizontal="center", vertical="center")
                cell.fill = PatternFill(start_color="DDDDDD", end_color="DDDDDD", fill_type="solid")

            # Add data rows
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

            # Auto-adjust column widths
            for col in ws.columns:
                max_length = 0
                column_letter = col[0].column_letter
                for cell in col:
                    if cell.value:
                        max_length = max(max_length, len(str(cell.value)))
                ws.column_dimensions[column_letter].width = max_length + 2

        # Fallback sheet if nothing matched
        if not wb.sheetnames:
            wb.create_sheet("No Data")
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