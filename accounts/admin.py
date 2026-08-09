from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'get_full_name', 'student_id', 'role', 'gender', 'is_active', 'date_joined')
    list_filter = ('role', 'gender', 'is_active', 'is_staff')
    search_fields = ('username', 'first_name', 'last_name', 'student_id', 'email', 'phone')
    ordering = ('-date_joined',)

    fieldsets = BaseUserAdmin.fieldsets + (
        (_('اطلاعات تکمیلی'), {
            'fields': ('student_id', 'phone', 'gender', 'role', 'avatar', 'is_active_student'),
        }),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        (_('اطلاعات تکمیلی'), {
            'fields': ('student_id', 'phone', 'gender', 'role'),
        }),
    )
