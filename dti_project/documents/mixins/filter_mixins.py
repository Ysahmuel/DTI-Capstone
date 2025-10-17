from django.db.models import Q

class FilterableDocumentMixin:
    """
    Adds filtering support for date ranges and status.
    """
    def apply_filters(self, qs):
        request = self.request
        start_date = request.GET.get("start_date")
        end_date = request.GET.get("end_date")
        statuses = request.GET.getlist("status")
        first_name = request.GET.get("first_name")
        last_name = request.GET.get("last_name")
        application_types = request.GET.getlist('application_type')

        filters = Q()
        model_fields = {f.name for f in qs.model._meta.get_fields()}

        # If application_type filter is active but this model doesn't have that field,
        # return empty queryset (exclude this model from results)
        if application_types and "application_type" not in model_fields:
            return qs.none()

        # If category filter is active but this model doesn't have that field, skip
        selected_categories = request.GET.getlist("category")
        if selected_categories and "category" not in model_fields:
            return qs.none()

        # If social_classification filter is active but this model doesn't have that field, skip
        selected_social = request.GET.getlist("social_classification")
        if selected_social and "social_classification" not in model_fields:
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

        # Handle user search safely
        if "user" in model_fields:
            user_filters = Q()
            if first_name:
                user_filters &= Q(user__first_name__icontains=first_name)
            if last_name:
                user_filters &= Q(user__last_name__icontains=last_name)
            filters &= user_filters

                
        # Handle application types
        if "application_type" in model_fields and application_types:
            filters &= Q(application_type__in=application_types)

        # Category filter
        if "category" in model_fields and selected_categories:
            filters &= Q(category__in=selected_categories)

        # Social classification filter
        if "social_classification" in model_fields and selected_social:
            filters &= Q(social_classification__in=selected_social)
        return qs.filter(filters)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        request = self.request

        context["selected_start_date"] = request.GET.get("start_date", "")
        context["selected_end_date"] = request.GET.get("end_date", "")
        context["selected_statuses"] = request.GET.getlist("status")
        context["selected_application_types"] = request.GET.getlist("application_type")

        # ServiceRepairAccreditationApplication-specific filters
        context["selected_categories"] = request.GET.getlist("category")
        context["selected_social_classifications"] = request.GET.getlist("social_classification")
        context["selected_asset_sizes"] = request.GET.getlist("asset_size")
        # Add the choice lists themselves for rendering checkboxes/radios
        if hasattr(ServiceRepairAccreditationApplication, "CATEGORIES"):
            context["CATEGORY_CHOICES"] = ServiceRepairAccreditationApplication.CATEGORIES
        if hasattr(ServiceRepairAccreditationApplication, "SOCIAL_CLASSIFICATION_CHOICES"):
            context["SOCIAL_CLASSIFICATION_CHOICES"] = ServiceRepairAccreditationApplication.SOCIAL_CLASSIFICATION_CHOICES
        return context