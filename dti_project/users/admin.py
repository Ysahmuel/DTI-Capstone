from django.contrib import admin
from .models import User

# Register your models here.

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'is_staff')
    list_filter = ('is_staff', )
    fields = ('first_name', 'last_name', 'email', 'is_active', 'is_staff')
    search_fields = ('first_name', 'last_name', 'email')