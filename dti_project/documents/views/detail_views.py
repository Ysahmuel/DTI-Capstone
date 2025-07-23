import re

from ..mixins import TabsSectionMixin
from ..constants import PERSONAL_DATA_SHEET_DETAIL_GROUPS, PERSONAL_DATA_SHEET_TAB_SECTIONS, SALES_PROMOTION_DETAIL_GROUPS
from ..models import PersonalDataSheet, SalesPromotionPermitApplication
from django.views.generic import DetailView

class SalesPromotionDetailView(DetailView):
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
    

    
class PersonalDataSheetDetailView(TabsSectionMixin, DetailView):
    template_name = 'documents/personal_data_sheet.html'
    model = PersonalDataSheet
    context_object_name = 'personal_data_sheet'
    
    # Enable lazy loading
    enable_lazy_loading = True
    tab_sections_config = PERSONAL_DATA_SHEET_TAB_SECTIONS

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['detail_groups'] = PERSONAL_DATA_SHEET_DETAIL_GROUPS

        return context