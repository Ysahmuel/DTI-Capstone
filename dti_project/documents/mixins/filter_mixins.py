from django.db.models import Q
from ..models.service_repair_accreditation_model import ServiceRepairAccreditationApplication

class FilterableDocumentMixin:
    """
    Adds filtering support for date ranges, status, application type,
    and other ServiceRepairAccreditationApplication-specific fields.
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
            "application_type": request.GET.getlist("application_type"),
            "category": request.GET.getlist("category"),
            "sex": request.GET.get("sex"),
            "social_classification": request.GET.getlist("social_classification"),
            "asset_size": request.GET.getlist("asset_size"),
            "form_of_organization": request.GET.getlist("form_of_organization"),
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

        # Date and status
        context["selected_start_date"] = request.GET.get("start_date", "")
        context["selected_end_date"] = request.GET.get("end_date", "")
        context["selected_statuses"] = request.GET.getlist("status")
        context["selected_application_types"] = request.GET.getlist("application_type")

        # ServiceRepairAccreditationApplication-specific filters
        context["selected_categories"] = request.GET.getlist("category")
        context["selected_social_classifications"] = request.GET.getlist("social_classification")
        context["selected_asset_sizes"] = request.GET.getlist("asset_size")
        context["selected_forms_of_organization"] = request.GET.getlist("form_of_organization")

        # Add the choice lists themselves for rendering checkboxes/radios
        if hasattr(ServiceRepairAccreditationApplication, "CATEGORIES"):
            context["CATEGORY_CHOICES"] = ServiceRepairAccreditationApplication.CATEGORIES
        if hasattr(ServiceRepairAccreditationApplication, "SOCIAL_CLASSIFICATION_CHOICES"):
            context["SOCIAL_CLASSIFICATION_CHOICES"] = ServiceRepairAccreditationApplication.SOCIAL_CLASSIFICATION_CHOICES
        if hasattr(ServiceRepairAccreditationApplication, "ASSET_SIZE_CHOICES"):
            context["ASSET_SIZE_CHOICES"] = ServiceRepairAccreditationApplication.ASSET_SIZE_CHOICES
        if hasattr(ServiceRepairAccreditationApplication, "FORM_OF_ORGANIZATION_CHOICES"):
            context["FORM_OF_ORGANIZATION_CHOICES"] = ServiceRepairAccreditationApplication.FORM_OF_ORGANIZATION_CHOICES

        return context
