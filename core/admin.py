from django.contrib import admin
from .models import SystemSettings, Notification


@admin.register(SystemSettings)
class SystemSettingsAdmin(admin.ModelAdmin):
    list_display = ('site_name', 'order_cutoff_hour', 'allow_student_charge', 'updated_at')


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'kind', 'title', 'is_read', 'created_at')
    list_filter = ('kind', 'is_read')
    search_fields = ('title', 'user__username')
