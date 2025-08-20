from django.http import JsonResponse
from django.shortcuts import render
from django.views.generic import TemplateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from documents.models import ChecklistEvaluationSheet, InspectionValidationReport, OrderOfPayment, PersonalDataSheet, SalesPromotionPermitApplication, ServiceRepairAccreditationApplication
from django.db.models import Value
from django.db.models import Value, F
from django.db.models.functions import Concat
from documents.constants import MODEL_URLS
from .forms import SearchForm
from users.models import User
    
# Create your views here.
class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "dashboard/dashboard.html"

    @staticmethod
    def get_queryset_or_all(model, user):
        qs = model.objects.exclude(status='draft') if user.role == 'admin' else model.objects.filter(user=user)
        
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
        user = request.user
        query = request.GET.get('query', '').strip()

        response_data = {
            'role': user.role,
            'users': [],
            'user_count': 0,
            'documents': {
                'results': [],
                'count': 0
            },
        }

        if not query:
            return JsonResponse(response_data)

        # Document models for both admin & business owners
        document_models = [
            SalesPromotionPermitApplication,
            PersonalDataSheet,
            ServiceRepairAccreditationApplication,
            OrderOfPayment,
            InspectionValidationReport,
            ChecklistEvaluationSheet,
        ]

        search_fields = [
            'promo_title', 'name_of_business', 'name',
            'first_name', 'middle_name', 'last_name'
        ]

        # --- ADMIN: search users + all documents ---
        if user.role == 'admin':
            # Users search
            users_qs = User.objects.annotate(
                full_name=Concat(F('first_name'), Value(' '), F('last_name'))
            ).filter(full_name__icontains=query).exclude(role="admin")

            response_data['users'] = [
                {
                    'id': u.id,
                    'full_name': u.full_name,
                    'profile_picture': u.profile_picture.url if u.profile_picture else '',
                    'role': u.role.replace('_', ' ').title()
                } for u in users_qs
            ]
            response_data['user_count'] = users_qs.count()

            # Admin: search ALL documents (no user restriction)
            for model in document_models:
                model_fields = [f.name for f in model._meta.fields]
                matched_field = None
                qs = model.objects.exclude(status='draft')

                if 'first_name' in model_fields and 'last_name' in model_fields:
                    qs = qs.annotate(
                        full_name=Concat(
                            F('first_name'),
                            Value(' '),
                            F('middle_name'),
                            Value(' '),
                            F('last_name')
                        )
                    )
                    matched_field = 'full_name'
                else:
                    for field in search_fields:
                        if field in model_fields:
                            matched_field = field
                            break

                if not matched_field:
                    continue

                qs = qs.filter(**{f'{matched_field}__icontains': query})

                serialized_docs = [
                    {
                        'id': obj.id,
                        'model': model._meta.verbose_name,  
                        'link': MODEL_URLS[model.__name__],
                        'display': getattr(obj, matched_field, str(obj))
                    }
                    for obj in qs
                ]

                response_data['documents']['results'].extend(serialized_docs)
                response_data['documents']['count'] += qs.count()

        # --- BUSINESS OWNER: only their own documents ---
        elif user.role == 'business_owner':
            for model in document_models:
                model_fields = [f.name for f in model._meta.fields]
                matched_field = None
                qs = model.objects.all()

                if 'first_name' in model_fields and 'last_name' in model_fields:
                    qs = qs.annotate(
                        full_name=Concat(
                            F('first_name'),
                            Value(' '),
                            F('middle_name'),
                            Value(' '),
                            F('last_name')
                        )
                    )
                    matched_field = 'full_name'
                else:
                    for field in search_fields:
                        if field in model_fields:
                            matched_field = field
                            break

                if not matched_field:
                    continue

                filter_kwargs = {f'{matched_field}__icontains': query}
                if 'user' in model_fields:  # restrict to owner
                    filter_kwargs['user'] = user

                qs = qs.filter(**filter_kwargs)

                serialized_docs = [
                    {
                        'id': obj.id,
                        'model': model._meta.verbose_name,
                        'link': MODEL_URLS[model.__name__],
                        'display': getattr(obj, matched_field, str(obj))
                    }
                    for obj in qs
                ]

                response_data['documents']['results'].extend(serialized_docs)
                response_data['documents']['count'] += qs.count()

        return JsonResponse(response_data)