from django.db.models import Q

from ..models.personal_data_sheet_model import PersonalDataSheet
from ..models.sales_promotion_model import SalesPromotionPermitApplication
from ..models.service_repair_accreditation_model import ServiceRepairAccreditationApplication

class FilterableDocumentMixin:
    """
    Adds filtering support for date ranges, status, and model-specific choice fields.
    """
    def apply_filters(self, qs):
        request = self.request
        start_date = request.GET.get("start_date")
        end_date = request.GET.get("end_date")
        statuses = request.GET.getlist("status")
        first_name = request.GET.get("first_name")
        last_name = request.GET.get("last_name")

        filters = Q()
        model_fields = {f.name for f in qs.model._meta.get_fields()}

        # Model-specific filters - if any are active but model doesn't have the field, skip
        model_specific_filters = {
            # ServiceRepairAccreditationApplication filters
            "application_type": request.GET.getlist("application_type"),
            "category": request.GET.getlist("category"),
            "social_classification": request.GET.getlist("social_classification"),
            "asset_size": request.GET.getlist("asset_size"),
            "form_of_organization": request.GET.getlist("form_of_organization"),
            # SalesPromotionPermitApplication filters
            "coverage": request.GET.getlist("coverage"),
            # PersonalDataSheet filters
            "civil_status": request.GET.getlist("civil_status"),
        }
        
        for field_name, filter_value in model_specific_filters.items():
            if filter_value and field_name not in model_fields:
                return qs.none()

        # Handle dates
        if "date" in model_fields:
            if start_date:
                filters &= Q(date__gte=start_date)
            if end_date:
                filters &= Q(date__lte=end_date)
        elif "date_filed" in model_fields:
            if start_date:
                filters &= Q(date_filed__gte=start_date)
            if end_date:
                filters &= Q(date_filed__lte=end_date)

        # Handle statuses
        if "status" in model_fields and statuses:
            filters &= Q(status__in=statuses)

        # Handle user search
        if "user" in model_fields:
            user_filters = Q()
            if first_name:
                user_filters &= Q(user__first_name__icontains=first_name)
            if last_name:
                user_filters &= Q(user__last_name__icontains=last_name)
            filters &= user_filters

        # Apply model-specific filters if field exists
        for field_name, filter_value in model_specific_filters.items():
            if field_name in model_fields and filter_value:
                filters &= Q(**{f"{field_name}__in": filter_value}) if isinstance(filter_value, list) else Q(**{field_name: filter_value})

        return qs.filter(filters)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        request = self.request

        # Common filters (available for all models)
        context["selected_start_date"] = request.GET.get("start_date", "")
        context["selected_end_date"] = request.GET.get("end_date", "")
        context["selected_statuses"] = request.GET.getlist("status")
        
        # Check which model-specific filters are active
        service_repair_filters_active = any([
            request.GET.getlist("application_type"),
            request.GET.getlist("category"),
            request.GET.getlist("social_classification"),
            request.GET.getlist("asset_size"),
            request.GET.getlist("form_of_organization"),
        ])
        
        sales_promo_filters_active = any([
            request.GET.getlist("coverage"),
        ])
        
        pds_filters_active = any([
            request.GET.getlist("civil_status"),
        ])
        
        # Determine which filters to show
        is_service_repair_view = (
            (hasattr(self, 'model') and self.model == ServiceRepairAccreditationApplication) or
            self.__class__.__name__ == 'AllDocumentListView' or
            service_repair_filters_active
        )
        
        is_sales_promo_view = (
            (hasattr(self, 'model') and self.model == SalesPromotionPermitApplication) or
            self.__class__.__name__ == 'AllDocumentListView' or
            sales_promo_filters_active
        )
        
        is_pds_view = (
            (hasattr(self, 'model') and self.model == PersonalDataSheet) or
            self.__class__.__name__ == 'AllDocumentListView' or
            pds_filters_active
        )
        
        context["show_service_repair_filters"] = is_service_repair_view
        context["show_sales_promo_filters"] = is_sales_promo_view
        context["show_pds_filters"] = is_pds_view
        
        # ServiceRepairAccreditationApplication filters
        if is_service_repair_view:
            context["selected_application_types"] = request.GET.getlist("application_type")
            context["selected_categories"] = request.GET.getlist("category")
            context["selected_social_classifications"] = request.GET.getlist("social_classification")
            context["selected_asset_sizes"] = request.GET.getlist("asset_size")
            context["selected_forms_of_organization"] = request.GET.getlist("form_of_organization")

            context["APPLICATION_TYPE_CHOICES"] = getattr(ServiceRepairAccreditationApplication, "APPLICATION_TYPE_CHOICES", [])
            context["CATEGORY_CHOICES"] = getattr(ServiceRepairAccreditationApplication, "CATEGORIES", [])
            context["SOCIAL_CLASSIFICATION_CHOICES"] = getattr(ServiceRepairAccreditationApplication, "SOCIAL_CLASSIFICATION_CHOICES", [])
            context["ASSET_SIZE_CHOICES"] = getattr(ServiceRepairAccreditationApplication, "ASSET_SIZE_CHOICES", [])
            context["FORM_OF_ORGANIZATION_CHOICES"] = getattr(ServiceRepairAccreditationApplication, "FORM_OF_ORGANIZATION_CHOICES", [])
        
        # SalesPromotionPermitApplication filters
        if is_sales_promo_view:
            context["selected_coverage"] = request.GET.getlist("coverage")
            context["COVERAGE_CHOICES"] = getattr(SalesPromotionPermitApplication, "COVERAGE_CHOICES", [])
        
        # PersonalDataSheet filters
        if is_pds_view:
            context["selected_civil_status"] = request.GET.getlist("civil_status")
            context["CIVIL_STATUS_CHOICES"] = getattr(PersonalDataSheet, "CIVIL_STATUS_CHOICES", [])

        return context
