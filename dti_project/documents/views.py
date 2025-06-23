from django.shortcuts import render
from django.views.generic import ListView, CreateView
from .forms import ProductCoveredFormSet, SalesPromotionPermitApplicationForm
from .models import ProductCovered, SalesPromotionPermitApplication

# Create your views here.
class CreateSalesPromotionView(CreateView):
    template_name = 'documents/create_sales_promotion.html'
    model = SalesPromotionPermitApplication
    context_object_name = 'sales_promo'
    form_class = SalesPromotionPermitApplicationForm

    def post(self, request, *args, **kwargs):
        pass

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['product_formset'] = ProductCoveredFormSet(self.request.POST, queryset=ProductCovered.objects.none())
        else:
            context['product_formset'] = ProductCoveredFormSet(queryset=ProductCovered.objects.none())
        return context
