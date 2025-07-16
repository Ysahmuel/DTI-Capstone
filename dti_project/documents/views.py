import re
from django.http import JsonResponse
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, DetailView
from .constants import PERSONAL_DATA_SHEET_FIELD_GROUPS, SALES_PROMOTION_FIELD_GROUPS, SERVICE_REPAIR_ACCREDITATION_FIELD_GROUPS
from .mixins import FormStepsMixin, FormsetMixin
from .forms import PersonalDataSheetForm, SalesPromotionPermitApplicationForm, FORMSET_CLASSES, ServiceRepairAccreditationApplicationForm
from .models import PersonalDataSheet, SalesPromotionPermitApplication, ServiceRepairAccreditationApplication
from django.contrib import messages
from django.db import transaction
from django.contrib.auth.mixins import LoginRequiredMixin

# Create your views here.from your_app.models import InspectionValidationReport
from datetime import date
from decimal import Decimal


class CreateSalesPromotionView(LoginRequiredMixin, FormStepsMixin, FormsetMixin, CreateView):
    template_name = 'documents/create_sales_promotion.html'
    model = SalesPromotionPermitApplication
    context_object_name = 'sales_promo'
    form_class = SalesPromotionPermitApplicationForm
    formset_classes = {
        'product': FORMSET_CLASSES['product_covered']
    }

    FIELD_GROUPS = SALES_PROMOTION_FIELD_GROUPS

    def get_context_data(self, **kwargs):
        context =  super().get_context_data(**kwargs)

        context['field_groups'] = self.FIELD_GROUPS


        return context
    
    def get_success_url(self):
        return reverse_lazy('sales-promotion-application', kwargs={'pk': self.object.pk})

class SalesPromotionDetailView(DetailView):
    model = SalesPromotionPermitApplication
    template_name = 'documents/sales_promotion_detail.html'
    context_object_name = 'sales_promo'

    def get_context_data(self, **kwargs):
        context =  super().get_context_data(**kwargs)
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
    
class CreatePersonalDataSheetView(LoginRequiredMixin, FormStepsMixin, FormsetMixin, CreateView):
    template_name = 'documents/create_personal_data_sheet.html'
    model = PersonalDataSheet
    form_class = PersonalDataSheetForm
    formset_classes = {
        'employee_background': FORMSET_CLASSES['employee_background'],
        'trainings_attended': FORMSET_CLASSES['trainings_attended'],
        'educational_attainment': FORMSET_CLASSES['educational_attainment'],
        'character_references': FORMSET_CLASSES['character_references'],
    }
    context_object_name = 'personal_data'

    FIELD_GROUPS = PERSONAL_DATA_SHEET_FIELD_GROUPS

    form_steps = [
        {'target': 'employee-fieldset', 'label': 'Employee Background'},
        {'target': 'training-fieldset', 'label': 'Trainings Attended'},
        {'target': 'educational-fieldset', 'label': 'Educational Attainment'},
        {'target': 'character-fieldset', 'label': 'Character References'},
    ]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['formsets_count'] = len(self.formset_classes) + 1
        context['field_groups'] = self.FIELD_GROUPS

        return context
    
    def get_success_url(self):
        return reverse_lazy('personal-data-sheet', kwargs={'pk': self.object.pk})
    
class PersonalDataSheetDetailView(DetailView):
    template_name = 'documents/personal_data_sheet.html'
    model = PersonalDataSheet
    context_object_name = 'personal_data_sheet'

    
class CreateServiceRepairAccreditationApplication(LoginRequiredMixin, FormStepsMixin, FormsetMixin, CreateView):
    template_name = 'documents/create_service_repair.html'
    model = ServiceRepairAccreditationApplication
    form_class = ServiceRepairAccreditationApplicationForm

    FIELD_GROUPS = SERVICE_REPAIR_ACCREDITATION_FIELD_GROUPS

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['field_groups'] = SERVICE_REPAIR_ACCREDITATION_FIELD_GROUPS
        
        # Create an unsaved instance with default values
        application = ServiceRepairAccreditationApplication(
            name_of_business=self.request.user,
            warranty_period=30  # Or whatever default
        )
        context['warranty_text'] = application.get_warranty_text()

        return context
    
