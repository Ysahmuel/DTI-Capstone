from .model_choices import SERVICE_CATEGORY_CHOICES, SERVICES_BY_CATEGORY
from .models import Service, ServiceCategory


def seed_services():
    for key, display_name in SERVICE_CATEGORY_CHOICES:
        category, _ = ServiceCategory.objects.get_or_create(key=key, defaults={"name": display_name})
        for service_name in SERVICES_BY_CATEGORY.get(key, []):
            Service.objects.get_or_create(category=category, name=service_name)