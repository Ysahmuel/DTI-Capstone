from django.http import JsonResponse
from django.shortcuts import render
from django.views.generic import TemplateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from documents.models import ChecklistEvaluationSheet, InspectionValidationReport, OrderOfPayment, PersonalDataSheet, SalesPromotionPermitApplication, ServiceRepairAccreditationApplication
from django.db.models import Value
from django.db.models import Value, F
from django.db.models.functions import Concat
from .forms import SearchForm
from users.models import User
    
# Create your views here.
class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "dashboard/dashboard.html"

    @staticmethod
    def get_queryset_or_all(model, user):
        qs = model.objects.all() if user.role == 'admin' else model.objects.filter(user=user)
        
        return qs.only('pk', 'id')  # Add other fields that __str__ methods need

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        context.update({
            'sales_promos': self.get_queryset_or_all(SalesPromotionPermitApplication, user),
            'personal_data_sheets': self.get_queryset_or_all(PersonalDataSheet, user),
            'service_accreditations': self.get_queryset_or_all(ServiceRepairAccreditationApplication, user),
            'inspection_reports': self.get_queryset_or_all(InspectionValidationReport, user),
            'orders_of_payment': self.get_queryset_or_all(OrderOfPayment, user),
            'checklist_evaluation_sheets': self.get_queryset_or_all(ChecklistEvaluationSheet, user),
        })

        return context
    
class SearchView(View):
    form_class = SearchForm
    pass

class SearchSuggestionsView(View):
    def get(self, request, *args, **kwargs):
        query = request.GET.get('query', '')
        user_results = []
        sales_promo_results = []

        if query:
            all_matching_users = User.objects.annotate(
                full_name=Concat(F('first_name'), Value(' '), F('last_name'))
            ).filter(full_name__icontains=query)

            user_suggestions = all_matching_users
            
            for user in user_suggestions:
                user_results.append({
                    'id': user.id,
                    'full_name': user.full_name,
                    'profile_picture': user.profile_picture.url
                })

            all_matching_sales_promos = SalesPromotionPermitApplication.objects.filter(promo_title__icontains=query)
            sales_promo_suggestions = all_matching_sales_promos

            for promo in sales_promo_suggestions:
                sales_promo_results.append({
                    'id': promo.id,
                    'title': promo.promo_title
                })


        return JsonResponse({
            'users': user_results,
            'user_count': all_matching_users.count(),
            'sales_promos': sales_promo_results,
            'sales_promo_count': all_matching_sales_promos.count()
        })