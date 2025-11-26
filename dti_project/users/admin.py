from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, ActivityLog


class UserAdmin(BaseUserAdmin):
    list_display = ('first_name', 'last_name', 'role', 'email', 'is_staff')
    list_filter = ('is_staff', 'role')
    search_fields = ('first_name', 'last_name', 'email')

    fieldsets = BaseUserAdmin.fieldsets + (
        ('Profile', {
            'fields': (
                'role',
                'profile_picture',
                'is_verified',
                'verification_code',
                'verification_code_expiration_date',
                'birthday',
                'dti_office',
                'official_designation',
            ),
        }),
    )

    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        (None, {
            'classes': ('wide',),
            'fields': (
                'role',
                'profile_picture',
                'is_verified',
                'verification_code',
                'verification_code_expiration_date'
            ),
        }),
    )

    def save_model(self, request, obj, form, change):
        # If superuser → force role to admin
        if obj.is_superuser:
            obj.role = 'admin'
        # If admin role → always staff
        if obj.role == "admin":
            obj.is_staff = True
        super().save_model(request, obj, form, change)

# register AFTER defining the class
admin.site.register(User, UserAdmin)

@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ("timestamp", "user", "action", "content_type", "object_id", "ip_address")
    list_filter = ("user", "content_type")
    search_fields = ("action", "object_id", "user__email", "user__first_name", "user__last_name")
    readonly_fields = ("timestamp", "user", "action", "content_type", "object_id", "ip_address", "extra")
    ordering = ("-timestamp",)