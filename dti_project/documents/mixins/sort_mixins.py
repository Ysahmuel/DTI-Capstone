import datetime
from django.db.models import Count

class SortMixin:
    """
    Mixin to handle sorting functionality for document list views.
    Works with both single querysets and combined/chained querysets.
    """
    default_sort_by = 'date'
    default_order = 'desc'
    
    def get_sort_params(self):
        """Get sort_by and order from request GET parameters"""
        sort_by = self.request.GET.get('sort_by', self.default_sort_by)
        order = self.request.GET.get('order', self.default_order)
        return sort_by, order
    
    def get_sort_key(self, obj):
        """
        Return the appropriate sort key for a document object.
        Handles both 'name' and 'date' sorting.
        """
        sort_by, _ = self.get_sort_params()
        
        if sort_by == 'name':
            # Sort by string representation of the object
            return str(obj).lower()
        else:  # sort_by == 'date'
            # Use the existing get_date_field logic
            return getattr(obj, "date_filed", None) or getattr(obj, "date", None) or datetime.date.min
    
    def apply_sorting(self, documents):
        """
        Apply sorting to documents (works with lists or querysets).
        Returns a sorted list.
        """
        sort_by, order = self.get_sort_params()
        reverse = (order == 'desc')
        
        # Convert to list if it's a queryset
        if hasattr(documents, 'model'):
            documents = list(documents)
        
        # Sort using the appropriate key
        return sorted(documents, key=self.get_sort_key, reverse=reverse)
    
    def get_context_data(self, **kwargs):
        """Add sort parameters to context"""
        context = super().get_context_data(**kwargs)
        sort_by, order = self.get_sort_params()
        context['sort_by'] = sort_by
        context['order'] = order
        return context
    
class SortCollectionReportListMixin:
    """
    Adds sorting functionality to CollectionReport list views.
    Supports sorting by:
    - 'number': Report number or report_collection_date
    - 'records': Number of report items
    """

    def get_queryset(self):
        qs = super().get_queryset()

        sort_by = self.request.GET.get("sort_by")
        order = self.request.GET.get("order", "asc")

        # Annotate with record count for sorting
        qs = qs.annotate(record_count=Count("report_items"))

        if sort_by == "number":
            sort_fields = ["report_no", "report_collection_date"]
        elif sort_by == "records":
            sort_fields = ["record_count"]
        else:
            sort_fields = ["-report_collection_date"]  # Default: latest first

        if order == "desc":
            sort_fields = [f"-{field}" for field in sort_fields]

        return qs.order_by(*sort_fields)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["sort_by"] = self.request.GET.get("sort_by", "")
        context["order"] = self.request.GET.get("order", "asc")
        return context
    
class SortCollectionReportListItemMixin:
    pass

class SortCollectionReportItemMixin:
    pass