from django.contrib import admin
from .models import PersonalDataSheet, ProductCovered, SalesPromotionPermitApplication

# Register your models here.
@admin.register(SalesPromotionPermitApplication)
class SalesPromotionAdmin(admin.ModelAdmin):
    list_display = ('promo_title', )
    search_fields = ('promo_title', 'sponsor_name', 'advertising_agency_name')
    
@admin.register(ProductCovered)
class ProductCoveredAdmin(admin.ModelAdmin):
    list_display = ('name', 'permit_application_title')
    search_fields = ('name', 'permit_application__promo_title')

    def permit_application_title(self, obj):
        return obj.permit_application.promo_title
    permit_application_title.short_description = 'Promo Title'

@admin.register(PersonalDataSheet)
class PersonalDataSheetAdmin(admin.ModelAdmin):
    list_display = ('last_name', 'first_name', 'email_address', 'sex')
    search_fields = ('last_name', 'first_name', 'email_address')
    list_filter = ('sex', 'civil_status')