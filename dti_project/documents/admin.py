from django.contrib import admin
from .models import SalesPromotionPermitApplication

# Register your models here.
@admin.register(SalesPromotionPermitApplication)
class SalesPromotionAdmin(admin.ModelAdmin):
    list_display = ('promo_title', )
    search_fields = ('promo_title', 'sponsor_name', 'advertising_agency_name')
    