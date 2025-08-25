import re

from ..mixins import TabsSectionMixin
from ..constants import CHECKLIST_EVALUATION_DETAIL_GROUPS, CHECKLIST_REQUIREMENT_GROUPS, INSPECTION_VALIDATION_DETAIL_GROUPS, ORDER_OF_PAYMENT_DETAIL_GROUPS, PERSONAL_DATA_SHEET_DETAIL_GROUPS, PERSONAL_DATA_SHEET_TAB_SECTIONS, SALES_PROMOTION_DETAIL_GROUPS, SERVICE_REPAIR_ACCREDITATION_DETAIL_GROUPS
from ..models import ChecklistEvaluationSheet, InspectionValidationReport, OrderOfPayment, PersonalDataSheet, SalesPromotionPermitApplication, ServiceRepairAccreditationApplication
from django.views.generic import DetailView
from django.contrib.auth.mixins import LoginRequiredMixin

class SalesPromotionDetailView(LoginRequiredMixin, DetailView):
    model = SalesPromotionPermitApplication
    template_name = 'documents/sales_promotion_detail.html'
    context_object_name = 'sales_promo'

    def get_context_data(self, **kwargs):
        context =  super().get_context_data(**kwargs)
        context['detail_groups'] = SALES_PROMOTION_DETAIL_GROUPS
        sales_promo = self.get_object()

        def split_locations(value):
            if value:
                return [item.strip() for item in re.split(r',|\n', value) if item.strip()]
            return []

        covered_locations = []
        coverage_type = None
        coverage_area_name = None  # for region_location_of_sponsor / single_region / single_province

        if sales_promo.coverage == 'NCR':
            coverage_type = 'NCR or several regions including Metro Manila'
            coverage_area_name = sales_promo.region_location_of_sponsor

        elif sales_promo.coverage == '2_REGIONS':
            coverage_type = '2 regions or more outside NCR'
            coverage_area_name = sales_promo.region_location_of_sponsor
            covered_locations = sales_promo.regions_covered

        elif sales_promo.coverage == '1_REGION_2_PROVINCES':
            coverage_type = 'Single region covering 2 provinces or more'
            coverage_area_name = sales_promo.single_region
            covered_locations = sales_promo.provinces_covered

        elif sales_promo.coverage == '1_PROVINCE':
            coverage_type = 'Single province'
            coverage_area_name = sales_promo.single_province
            covered_locations = sales_promo.cities_or_municipalities_covered

        context.update({
            'covered_locations': covered_locations,
            'location_count': len(split_locations(covered_locations)),
            'coverage_type': coverage_type,
            'coverage_area_name': coverage_area_name,
        })

        return context
    
class PersonalDataSheetDetailView(TabsSectionMixin, LoginRequiredMixin, DetailView):
    template_name = 'documents/personal_data_sheet.html'
    model = PersonalDataSheet
    context_object_name = 'personal_data_sheet'
    
    # Enable lazy loading
    enable_lazy_loading = True
    tab_sections_config = PERSONAL_DATA_SHEET_TAB_SECTIONS

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['detail_groups'] = PERSONAL_DATA_SHEET_DETAIL_GROUPS
        context["update_url_name"] = "update-personal-data-sheet"

        return context

class ServiceRepairAccreditationApplicationDetailView(LoginRequiredMixin, DetailView):
    template_name = 'documents/service_repair_accreditation.html'
    model = ServiceRepairAccreditationApplication
    context_object_name = 'accreditation'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['detail_groups'] = SERVICE_REPAIR_ACCREDITATION_DETAIL_GROUPS
        context["update_url_name"] = "update-service-repair-accreditation"

        return context
    
class InspectionValidationReportDetailView(LoginRequiredMixin, DetailView):
    template_name = 'documents/inspection_validation_report.html'
    model = InspectionValidationReport
    context_object_name = 'report'

    # Enable lazy loading
    enable_lazy_loading = True

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['detail_groups'] = INSPECTION_VALIDATION_DETAIL_GROUPS
        context['services_by_category'] = self.object.group_services_by_category()

        return context
    
class OrderOfPaymentDetailView(LoginRequiredMixin, DetailView):
    template_name = 'documents/order_of_payment.html'
    model = OrderOfPayment
    context_object_name = 'order'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        order = self.object  # Get the current OrderOfPayment instance

        remark_prefixes = [
            "discount", "premium", "raffle", "contest",
            "redemption", "games", "beauty_contest",
            "home_solicitation", "amendments"
        ]

        permit_fees = []
        for prefix in remark_prefixes:
            permit_fees.append({
                "label": prefix.replace("_", " ").title(),
                "amount": getattr(order, f"{prefix}_amount") or 0,
                "remark": getattr(order, f"get_{prefix}_remark_display")(),
            })

        context['detail_groups'] = ORDER_OF_PAYMENT_DETAIL_GROUPS
        context['remark_prefixes'] = remark_prefixes
        context['permit_fees'] = permit_fees
        context["update_url_name"] = "update-order-of-payment"

        return context

class ChecklistEvaluationSheetDetailView(LoginRequiredMixin, DetailView):
    template_name = 'documents/checklist_evaluation_sheet.html'
    model = ChecklistEvaluationSheet
    context_object_name = 'checklist_sheet'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['detail_groups'] = CHECKLIST_EVALUATION_DETAIL_GROUPS
        context['requirement_groups'] = CHECKLIST_REQUIREMENT_GROUPS
        context["update_url_name"] = "update-checklist-evaluation-sheet"

        return context