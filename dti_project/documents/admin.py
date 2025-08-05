from django.contrib import admin
from .utils.admin_helpers import get_full_name_from_personal_data
from .models import CharacterReference, EducationalAttainment, EmployeeBackground, InspectionValidationReport, OrderOfPayment, PersonalDataSheet, ProductCovered, SalesPromotionPermitApplication, Service, ServiceCategory, ServiceRepairAccreditationApplication, TrainingsAttended


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

@admin.register(EmployeeBackground)
class EmployeeBackgroundAdmin(admin.ModelAdmin):
    list_display = (get_full_name_from_personal_data, 'employer', 'position', 'start_date', 'end_date')
    search_fields = ('employer', 'position')

@admin.register(TrainingsAttended)
class TrainingsAttendedAdmin(admin.ModelAdmin):
    list_display = (get_full_name_from_personal_data, 'training_course', 'conducted_by')
    search_fields = ('training_course', 'conducted_by')

@admin.register(EducationalAttainment)
class EducationalAttainmentAdmin(admin.ModelAdmin):
    list_display = (get_full_name_from_personal_data, 'school', 'course')
    search_fields = ('school', 'course')

@admin.register(CharacterReference)
class CharacterReferencesAdmin(admin.ModelAdmin):
    list_display = ('name', 'company', 'email', 'contact_number')
    search_fields = ('name', 'company')

@admin.register(ServiceRepairAccreditationApplication)
class ServiceRepairAccreditationApplicationAdmin(admin.ModelAdmin):
    list_display = ('name_of_business', 'full_name', 'application_type', 'category', 'star_rating')
    search_fields = ('name_of_business', 'first_name', 'last_name')
    list_filter = ('application_type', 'category', 'star_rating', 'social_classification', 'asset_size', 'form_of_organization')

    def full_name(self, obj):
        return f"{obj.first_name} {obj.middle_name or ''} {obj.last_name}".strip()
    
    full_name.short_description = 'Full Name'

@admin.register(OrderOfPayment)
class OrderOfPaymentAdmin(admin.ModelAdmin):
    list_display = ('name', 'date')
    search_fields = ('name', )

@admin.register(InspectionValidationReport)
class InspectionValidationReportAdmin(admin.ModelAdmin):
    list_display = ('name_of_business', 'type_of_application_activity', 'date')
    search_fields = ('name_of_business', 'address')
    list_filter = ('type_of_application_activity', 'date')
    date_hierarchy = 'date'
    ordering = ['-date']


@admin.register(ServiceCategory)
class ServiceCategoryAdmin(admin.ModelAdmin):
    list_display = ('key', 'name')
    search_fields = ('key', 'name')
    ordering = ['key']


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'category')
    list_filter = ('category',)
    search_fields = ('name',)
    ordering = ['category', 'name']