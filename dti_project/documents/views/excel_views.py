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
from django.db.models import Q

class ImportFromExcelView(View):
    pass

@login_required
def export_to_excel(request, queryset=None, filename="export.xlsx"):
    """
    Reusable export function that can be called:
    1. As a Django view (Django passes request, queryset=None).
    2. As a helper by passing your own queryset explicitly.
    """
    if queryset is None:
        user = request.user
        
        # Get filter parameters from URL
        doc_type = request.GET.get('doc_type', 'all')
        search = request.GET.get('search', '')
        date_from = request.GET.get('date_from', '')
        date_to = request.GET.get('date_to', '')
        
        # If no doc_type in GET params, try to infer from the referer URL
        if doc_type == 'all' and 'HTTP_REFERER' in request.META:
            referer_path = request.META['HTTP_REFERER']
            if 'sales-promotion' in referer_path:
                doc_type = 'sales_promos'
            elif 'personal-data-sheet' in referer_path:
                doc_type = 'personal_data_sheets'
            elif 'service-repair' in referer_path:
                doc_type = 'service_accreditations'
            elif 'inspection-validation' in referer_path:
                doc_type = 'inspection_reports'
            elif 'order-of-payment' in referer_path:
                doc_type = 'orders_of_payment'
            elif 'checklist-evaluation' in referer_path:
                doc_type = 'checklist_evaluation_sheets'
        
        # Convert date strings to date objects if provided
        date_from_obj = None
        date_to_obj = None
        if date_from:
            try:
                date_from_obj = datetime.strptime(date_from, '%Y-%m-%d').date()
            except ValueError:
                pass
        
        if date_to:
            try:
                date_to_obj = datetime.strptime(date_to, '%Y-%m-%d').date()
            except ValueError:
                pass
        
        # Helper function to apply filters to a queryset
        def apply_filters(qs):
            if search:
                # Apply search filter
                qs = qs.filter(
                    Q(user__username__icontains=search) | 
                    Q(id__icontains=search)
                )
            
            if date_from_obj:
                # Apply date from filter
                qs = qs.filter(
                    Q(date_filed__gte=date_from_obj) | Q(date__gte=date_from_obj)
                )
            
            if date_to_obj:
                # Apply date to filter
                qs = qs.filter(
                    Q(date_filed__lte=date_to_obj) | Q(date__lte=date_to_obj)
                )
            
            return qs
        
        # Apply filters based on current page context
        if doc_type == 'sales_promos':
            base_qs = UserRoleMixin.get_queryset_or_all(SalesPromotionPermitApplication, user)
            queryset = apply_filters(base_qs)
            
        elif doc_type == 'personal_data_sheets':
            base_qs = UserRoleMixin.get_queryset_or_all(PersonalDataSheet, user)
            queryset = apply_filters(base_qs)
            
        elif doc_type == 'service_accreditations':
            base_qs = UserRoleMixin.get_queryset_or_all(ServiceRepairAccreditationApplication, user)
            queryset = apply_filters(base_qs)
            
        elif doc_type == 'inspection_reports':
            base_qs = UserRoleMixin.get_queryset_or_all(InspectionValidationReport, user)
            queryset = apply_filters(base_qs)
            
        elif doc_type == 'orders_of_payment':
            base_qs = UserRoleMixin.get_queryset_or_all(OrderOfPayment, user)
            queryset = apply_filters(base_qs)
            
        elif doc_type == 'checklist_evaluation_sheets':
            base_qs = UserRoleMixin.get_queryset_or_all(ChecklistEvaluationSheet, user)
            queryset = apply_filters(base_qs)
            
        else:  # 'all' or default
            # Get all individual querysets and apply filters to each
            sales_promos = apply_filters(UserRoleMixin.get_queryset_or_all(SalesPromotionPermitApplication, user))
            personal_data_sheets = apply_filters(UserRoleMixin.get_queryset_or_all(PersonalDataSheet, user))
            service_accreditations = apply_filters(UserRoleMixin.get_queryset_or_all(ServiceRepairAccreditationApplication, user))
            inspection_reports = apply_filters(UserRoleMixin.get_queryset_or_all(InspectionValidationReport, user))
            orders_of_payment = apply_filters(UserRoleMixin.get_queryset_or_all(OrderOfPayment, user))
            checklist_evaluation_sheets = apply_filters(UserRoleMixin.get_queryset_or_all(ChecklistEvaluationSheet, user))
            
            # Chain them together
            queryset = chain(
                sales_promos, personal_data_sheets, service_accreditations,
                inspection_reports, orders_of_payment, checklist_evaluation_sheets,
            )

    # Build Excel
    wb = Workbook()
    ws = wb.active
    ws.title = "Export"
    ws.append(["Document Type", "ID", "Filed By", "Date Filed"])

    for doc in queryset:
        doc_type = doc._meta.verbose_name
        doc_id = getattr(doc, "id", "")
        filed_by = getattr(doc, "user", None)
        date_filed = getattr(doc, "date_filed", None) or getattr(doc, "date", "")
        ws.append([doc_type, str(doc_id), str(filed_by), str(date_filed)])

    # Return response
    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = f'attachment; filename={filename}'
    wb.save(response)
    return response