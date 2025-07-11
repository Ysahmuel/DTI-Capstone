from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User

class UserAdmin(BaseUserAdmin):
    list_display = ('first_name', 'last_name', 'email', 'is_staff')
    list_filter = ('is_staff', )
    search_fields = ('first_name', 'last_name', 'email')

    # Extend the default fieldsets to include profile_picture
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Profile', {
            'fields': ('profile_picture',),
        }),
    )

admin.site.register(User, UserAdmin)
