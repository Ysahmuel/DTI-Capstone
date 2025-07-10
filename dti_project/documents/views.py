import re
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, DetailView
from .mixins import FormStepsMixin, FormsetMixin
from .forms import PersonalDataSheetForm, SalesPromotionPermitApplicationForm, FORMSET_CLASSES
from .models import PersonalDataSheet, ProductCovered, SalesPromotionPermitApplication
from django.contrib import messages
from django.db import transaction
from django.contrib.auth.mixins import LoginRequiredMixin

# Create your views here.
class CreateSalesPromotionView(LoginRequiredMixin, FormStepsMixin, FormsetMixin, CreateView):
    template_name = 'documents/create_sales_promotion.html'
    model = SalesPromotionPermitApplication
    context_object_name = 'sales_promo'
    form_class = SalesPromotionPermitApplicationForm
    formset_classes = {
        'product': FORMSET_CLASSES['product_covered']
    }

    form_steps = [
        {'target': 'promo-title-fieldset', 'label': 'Promotion Details'},
        {'target': 'sponsors-fieldset', 'label': 'Sponsor'},
        {'target': 'advertising-fieldset', 'label': 'Advertising Agency'},
        {'target': 'promo-period-fieldset', 'label': 'Promo Period'},
        {'target': 'products-fieldset', 'label': 'Products Covered'},
        {'target': 'coverage-fieldset', 'label': 'Coverage'},
    ]
    
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

    form_steps = [
        {'target': 'personal-background-fieldset', 'label': 'Personal Background'},
        {'target': 'employee-fieldset', 'label': 'Employee Background'},
        {'target': 'training-fieldset', 'label': 'Trainings Attended'},
    ]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
    
        return context