from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView
from .forms import ProductCoveredFormSet, SalesPromotionPermitApplicationForm
from .models import ProductCovered, SalesPromotionPermitApplication
from django.contrib import messages
from django.db import transaction

# Create your views here.
class CreateSalesPromotionView(CreateView):
    template_name = 'documents/create_sales_promotion.html'
    model = SalesPromotionPermitApplication
    context_object_name = 'sales_promo'
    form_class = SalesPromotionPermitApplicationForm
    success_url = reverse_lazy('dashboard')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['product_formset'] = ProductCoveredFormSet(self.request.POST, queryset=ProductCovered.objects.none())
        else:
            context['product_formset'] = ProductCoveredFormSet(queryset=ProductCovered.objects.none())

        # For dynamic reusable progress indicator partial template
        context['form_steps'] = [
            {'target': 'promo-title-fieldset', 'label': 'Promotion Details'},
            {'target': 'sponsors-fieldset', 'label': 'Sponsor'},
            {'target': 'advertising-fieldset', 'label': 'Advertising Agency'},
            {'target': 'promo-period-fieldset', 'label': 'Promo Period'},
            {'target': 'products-fieldset', 'label': 'Products Covered'},
            {'target': 'coverage-fieldset', 'label': 'Coverage'},
        ]
        
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        product_formset = context['product_formset']

        # Use transaction to ensure data integrity
        with transaction.atomic():
            # Save the main form first
            self.object = form.save()

            if product_formset.is_valid():
                # Save formset instances with the relationship
                instances = product_formset.save(commit=False)
                for instance in instances:
                    # Assuming ProductCovered has a ForeignKey to SalesPromotionPermitApplication
                    instance.sales_promotion = self.object
                    instance.save()

                # Handle any deletions
                product_formset.save_m2m()

                messages.success(
                    self.request,
                    'Sales Promotion Permit Application created successfully!'
                )
                return super().form_valid(form)
            else:
                # If formset is invalid, return to form with errors
                return self.form_invalid(form)
            
    def form_invalid(self, form):
        messages.error(self.request, 'Please correct the errors below.')
        return super().form_invalid()