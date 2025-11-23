import datetime
import re
from urllib.parse import quote
from django.views import View
from django.apps import apps
from django.http import HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from openpyxl.utils import get_column_letter
from io import BytesIO
from zipfile import ZipFile
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, Image, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
import matplotlib
matplotlib.use('Agg')  # Non-GUI backend suitable for server-side plotting
import matplotlib.pyplot as plt
from reportlab.platypus import Image, Paragraph, Spacer
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import PageBreak
from reportlab.lib.pagesizes import landscape, A4
from ..mixins.filter_mixins import FilterableDocumentMixin
from ..models.base_models import DraftModel
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

    def export_excel(self):
        from openpyxl.utils import get_column_letter

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

            model_verbose_name = model._meta.verbose_name
            included_models.append(model_verbose_name)

            sheet_title = clean_sheet_name(model_verbose_name)
            ws = wb.create_sheet(title=sheet_title)

            fields = [f for f in model._meta.get_fields() if f.concrete and not f.many_to_many and f.name != 'id']
            headers = [to_title(f.verbose_name) for f in fields]
            num_cols = len(headers)

            # Header section
            ws.merge_cells('F1:I1'); ws['F1'].value = f"{to_title(model_verbose_name)} Report"; ws['F1'].font = Font(bold=True, size=12)
            ws.merge_cells('F2:I2'); ws['F2'].value = "DTI Albay Provincial Office"; ws['F2'].font = Font(bold=True, size=10)
            ws.merge_cells('F3:I3'); ws['F3'].value = datetime.date.today().strftime("%B %d, %Y"); ws['F3'].font = Font(size=10)
            ws.row_dimensions[4].height = 10
            thick_border = Border(bottom=Side(style='thick', color='000000'))
            for col_num in range(1, num_cols + 1):
                ws.cell(row=4, column=col_num).border = thick_border

            # Column headers row 5
            for col_num, header in enumerate(headers, 1):
                cell = ws.cell(row=5, column=col_num)
                cell.value = header
                cell.font = Font(bold=True, size=10)
                cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
                cell.border = Border(top=Side(style='thin', color='000000'),
                                     bottom=Side(style='thin', color='000000'),
                                     left=Side(style='thin', color='000000'),
                                     right=Side(style='thin', color='000000'))

            # Data rows
            current_row = 6
            for obj in objs:
                row = []
                for f in fields:
                    val = getattr(obj, f.name, "")
                    if isinstance(val, datetime.datetime):
                        val = val.date()
                    if val is None:
                        val = ""
                    row.append(to_title(str(val)) if val != "" else "")
                for col_num, value in enumerate(row, 1):
                    cell = ws.cell(row=current_row, column=col_num)
                    cell.value = value
                    cell.font = Font(size=9)
                    cell.alignment = Alignment(horizontal="left", vertical="top", wrap_text=True)
                    cell.border = Border(top=Side(style='thin', color='CCCCCC'),
                                         bottom=Side(style='thin', color='CCCCCC'),
                                         left=Side(style='thin', color='CCCCCC'),
                                         right=Side(style='thin', color='CCCCCC'))
                current_row += 1

            # Auto-fit columns
            for col_num in range(1, num_cols + 1):
                max_length = 0
                column_letter = get_column_letter(col_num)
                for row_num in range(5, current_row):
                    cell = ws.cell(row=row_num, column=col_num)
                    if cell.value:
                        max_length = max(max_length, len(str(cell.value)))
                ws.column_dimensions[column_letter].width = min(max(max_length + 2, 10), 50)

        # Fallback sheet
        if not wb.sheetnames:
            ws = wb.create_sheet("No Data")
            ws['A1'] = "No Data Available"
            ws['A1'].font = Font(size=10)

        excel_buffer = BytesIO()
        wb.save(excel_buffer)
        excel_buffer.seek(0)
        return excel_buffer

    def export_pdf(self):
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=landscape(A4),
            leftMargin=30, rightMargin=30, topMargin=30, bottomMargin=30
        )
        elements = []
        styles = getSampleStyleSheet()

        # Header
        elements.append(Paragraph("Documents Report", styles['Title']))
        elements.append(Paragraph("DTI Albay Provincial Office", styles['Heading2']))
        elements.append(Paragraph(f"Generated on: {datetime.date.today().strftime('%B %d, %Y')}", styles['Normal']))
        elements.append(Spacer(1, 12))

        # Collect document info
        MODEL_MAP = {
            model._meta.model_name: model
            for model in apps.get_models()
            if issubclass(model, DraftModel) and not model._meta.abstract
        }

        doc_type_counts = {}
        status_counts = {}
        date_samples = []

        DOC_SPECIFIC_FIELDS = {
            "salespromotionpermitapplication": ["coverage"],
            "inspectionvalidationreport": ["type_of_application_activity"],
            "checklistevaluationsheet": ["type_of_application", "star_rating"],
            "servicerepairaccreditationapplication": [
                "application_type", "category", "star_rating",
                "social_classification", "asset_size", "form_of_organization"
            ],
            "personaldatasheet": ["sex", "civil_status", "nationality"],  
        }

        doc_specific_data = {}

        for model_name, model in MODEL_MAP.items():
            qs = self.apply_filters(model.objects.all())
            objs = list(qs)
            if not objs:
                continue

            model_verbose_name = to_title(model._meta.verbose_name)
            doc_type_counts[model_verbose_name] = len(objs)

            # Collect dates
            date_fields = [f.name for f in model._meta.fields if f.get_internal_type() in ['DateField', 'DateTimeField']]
            for f in date_fields:
                for o in objs:
                    val = getattr(o, f, None)
                    if val:
                        date_samples.append(val)

            # Status
            if hasattr(model, 'status'):
                for o in objs:
                    status = getattr(o, 'status', 'Unknown')
                    status_counts[status] = status_counts.get(status, 0) + 1

            # Document-specific fields
            key = model_name.lower()
            if key in DOC_SPECIFIC_FIELDS:
                for field in DOC_SPECIFIC_FIELDS[key]:
                    values_count = {}
                    for o in objs:
                        val = getattr(o, field, None)
                        if val is not None:
                            if field == "star_rating":
                                val = f"{val} Star"
                            values_count[val] = values_count.get(val, 0) + 1
                    doc_specific_data[f"{model_verbose_name} - {to_title(field)}"] = values_count

        # Sample size
        if date_samples:
            # Convert all to datetime.date
            date_only_samples = [
                d.date() if isinstance(d, datetime.datetime) else d
                for d in date_samples
            ]
            oldest = min(date_only_samples)
            newest = max(date_only_samples)
            elements.append(Paragraph(
                f"Sample Size: {len(date_only_samples)} documents ({oldest} - {newest})",
                styles['Normal']
            ))
            elements.append(Spacer(1,12))

        # Helper function for charts
        def build_pie_chart(counts_dict):
            labels = list(counts_dict.keys())
            sizes = list(counts_dict.values())
            cmap = plt.get_cmap("tab20")
            colors_list = [cmap(i) for i in range(len(sizes))]
            hex_colors = [f'#{int(r*255):02X}{int(g*255):02X}{int(b*255):02X}' for r,g,b,_ in colors_list]

            # Square pie chart
            fig, ax = plt.subplots(figsize=(2.5,2.5))
            ax.pie(sizes, labels=None, colors=colors_list, startangle=90)
            ax.axis('equal')
            plt.tight_layout(pad=0.1)
            buf = BytesIO()
            plt.savefig(buf, format='PNG', bbox_inches='tight')
            plt.close(fig)
            buf.seek(0)

            # Bullet points
            bullet_style = ParagraphStyle('BulletStyle', fontSize=9, leftIndent=10, spaceAfter=2)
            total = sum(sizes)
            bullets = [Paragraph(
                f'<font color="{hex_colors[i]}">&#9679;</font> {labels[i]}: {sizes[i]} ({sizes[i]/total*100:.1f}%)',
                bullet_style
            ) for i in range(len(labels))]
            return buf, bullets

        # Combine all charts
        charts_data = []

        if doc_type_counts:
            buf, bullets = build_pie_chart(doc_type_counts)
            charts_data.append((buf, bullets, "Document Types"))

        if status_counts:
            buf, bullets = build_pie_chart(status_counts)
            charts_data.append((buf, bullets, "Statuses"))

        for title, data in doc_specific_data.items():
            if data:
                buf, bullets = build_pie_chart(data)
                charts_data.append((buf, bullets, title))

        # Layout: 2 charts per row (left + right)
        for i in range(0, len(charts_data), 2):
            row_data = []
            for j in range(2):
                if i+j < len(charts_data):
                    buf, bullets, title = charts_data[i+j]
                    # Table with title, chart, bullets
                    chart_table = Table([
                        [Paragraph(title, styles['Heading3'])],
                        [Image(buf, width=150, height=150)],
                        [bullets]
                    ])
                    chart_table.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'TOP')]))
                    row_data.append(chart_table)
                else:
                    row_data.append("")  # empty cell
            page_table = Table([row_data], colWidths=[doc.width/2.0]*2)
            page_table.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'TOP')]))
            elements.append(page_table)
            elements.append(Spacer(1,24))

        doc.build(elements)
        buffer.seek(0)
        return buffer

    def post(self, request, *args, **kwargs):
        excel_buffer = self.export_excel()
        pdf_buffer = self.export_pdf()

        zip_buffer = BytesIO()
        with ZipFile(zip_buffer, 'w') as zip_file:
            zip_file.writestr(f"Documents Report {datetime.date.today()}.xlsx", excel_buffer.getvalue())
            zip_file.writestr(f"Documents Report {datetime.date.today()}.pdf", pdf_buffer.getvalue())

        zip_buffer.seek(0)
        response = HttpResponse(zip_buffer, content_type='application/zip')
        response['Content-Disposition'] = f'attachment; filename="Documents Report {datetime.date.today()}.zip"'
        return response