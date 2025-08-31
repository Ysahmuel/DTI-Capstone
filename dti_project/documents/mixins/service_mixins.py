from ..models import ServiceCategory


class ServiceCategoryMixin:
    def get_service_categories_with_services(self):
        """
        Returns a list of service categories, each with their related services.
        Format: [
            {
                "category": <ServiceCategory instance>,
                "services": [<Service instance>, ...]
            },
            ...
        ]
        """
        categories = ServiceCategory.objects.prefetch_related('services')
        return [
            {
                "category": category,
                "services": category.services.all()
            }
            for category in categories
        ]
