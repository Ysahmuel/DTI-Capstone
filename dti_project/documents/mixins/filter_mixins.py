from django.db.models import Q, Min, Max


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
    
class FilterCollectionReportListMixin:
    """
    Adds filtering for CollectionReport objects.
    Supports:
      - report_collection_date range (start_date / end_date)
      - duration_type (Daily, Monthly, Yearly) computed via model.report_duration()
    """

    def apply_filters(self, qs):
        request = self.request

        # --- Filter params ---
        start_date = request.GET.get("start_date")
        end_date = request.GET.get("end_date")
        duration_type = request.GET.get("duration_type")

        filters = Q()

        # --- Date filters (based on report_collection_date) ---
        if start_date:
            filters &= Q(report_collection_date__gte=start_date)
        if end_date:
            filters &= Q(report_collection_date__lte=end_date)

        # Apply DB-side filters first
        qs = qs.filter(filters).distinct()

        # --- Duration Type filter (computed via model method) ---
        if duration_type:
            # Build list of matching IDs (computed property can't be queried in DB)
            matching_ids = [
                r.id for r in qs if r.report_duration().lower() == duration_type.lower()
            ]
            # Keep it a queryset so pagination/order_by/etc still work
            qs = qs.filter(id__in=matching_ids)

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        request = self.request

        # Preserve selected filter values
        context.update({
            "selected_start_date": request.GET.get("start_date", ""),
            "selected_end_date": request.GET.get("end_date", ""),
            "selected_duration_type": request.GET.get("duration_type", ""),
        })

        # --- Compute min/max report_collection_date for date input min/max attributes ---
        ModelClass = self.model  # keep mixin generic
        agg = ModelClass._base_manager.aggregate(
            min_date=Min("report_collection_date"),
            max_date=Max("report_collection_date"),
        )

        min_date = agg["min_date"]
        max_date = agg["max_date"]

        context["min_report_date"] = min_date or ""
        context["max_report_date"] = max_date or ""
        context["min_report_date_iso"] = min_date.isoformat() if min_date else ""
        context["max_report_date_iso"] = max_date.isoformat() if max_date else ""

        return context
    
class FilterCollectionReportListItemMixin:
    """
    Adds filtering for CollectionReportItem objects.
    Supports:
    - Date range (date)
    - Payor
    - Particulars (dropdown based on existing values)
    - Amount range
    """
    
    def apply_filters(self, qs):
        request = self.request

        start_date = request.GET.get("start_date")
        end_date = request.GET.get("end_date")
        payor = request.GET.get("payor")
        particulars = request.GET.get("particulars")
        min_amount = request.GET.get("min_amount")
        max_amount = request.GET.get("max_amount")

        filters = Q()

        # Date range filter
        if start_date:
            filters &= Q(date__gte=start_date)
        if end_date:
            filters &= Q(date__lte=end_date)

        # String search filters
        if payor:
            filters &= Q(payor__icontains=payor)
        if particulars:
            filters &= Q(particulars=particulars)  # exact match for dropdown

        # Numeric filters
        if min_amount:
            filters &= Q(amount__gte=min_amount)
        if max_amount:
            filters &= Q(amount__lte=max_amount)

        return qs.filter(filters)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        request = self.request

        # Preserve selected filters in template
        context["selected_start_date"] = request.GET.get("start_date", "")
        context["selected_end_date"] = request.GET.get("end_date", "")
        context["selected_payor"] = request.GET.get("payor", "")
        context["selected_particulars"] = request.GET.get("particulars", "")
        context["selected_min_amount"] = request.GET.get("min_amount", "")
        context["selected_max_amount"] = request.GET.get("max_amount", "")

        return context