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

        filters = Q()
        model_fields = {f.name for f in qs.model._meta.get_fields()}

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

                
        # Handle application types
        if "application_type" in model_fields and application_types:
            filters &= Q(application_type__in=application_types)

        return qs.filter(filters)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        request = self.request

        context["selected_start_date"] = request.GET.get("start_date", "")
        context["selected_end_date"] = request.GET.get("end_date", "")
        context["selected_statuses"] = request.GET.getlist("status")

        return context