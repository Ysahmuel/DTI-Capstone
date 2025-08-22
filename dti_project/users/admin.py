# admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User

class UserAdmin(BaseUserAdmin):
    list_display = ('first_name', 'last_name', 'role', 'email', 'is_staff')
    list_filter = ('is_staff', 'role')
    search_fields = ('first_name', 'last_name', 'email')

    # Extend the default fieldsets to include role + profile_picture
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Profile', {
            'fields': ('role', 'profile_picture', 'is_verified', 'verification_code', 'verification_code_expiration_date'),
        }),
    )

    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        (None, {
            'classes': ('wide',),
            'fields': ('role', 'profile_picture', 'is_verified', 'verification_code', 'verification_code_expiration_date'),
        }),
    )

    def save_model(self, request, obj, form, change):
        # If user is created as superuser → force role to "admin"
        if obj.is_superuser:
            obj.role = 'admin'

        # If role is admin → make sure they have staff access
        if obj.role == "admin":
            obj.is_staff = True

        super().save_model(request, obj, form, change)

admin.site.register(User, UserAdmin)
