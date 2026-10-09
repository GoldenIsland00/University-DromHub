from django.contrib import admin
from .models import AccessLog, Building, Room, Bed


class BedInline(admin.TabularInline):
    model = Bed
    extra = 0
    fields = ('number', 'occupant')
    autocomplete_fields = ['occupant']


class RoomInline(admin.TabularInline):
    model = Room
    extra = 0
    fields = ('number', 'floor', 'capacity', 'is_active')


@admin.register(Building)
class BuildingAdmin(admin.ModelAdmin):
    list_display = ('name', 'section', 'floors')
    list_filter = ('section',)
    inlines = [RoomInline]


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('number', 'building', 'floor', 'capacity', 'occupied_count', 'is_active')
    list_filter = ('building__section', 'building', 'floor', 'is_active')
    search_fields = ('number', 'building__name')
    inlines = [BedInline]


@admin.register(Bed)
class BedAdmin(admin.ModelAdmin):
    list_display = ('room', 'number', 'occupant')
    list_filter = ('room__building__section', 'room__building')
    search_fields = ('room__number', 'occupant__username', 'occupant__first_name')
    autocomplete_fields = ['occupant', 'room']


@admin.register(AccessLog)
class AccessLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'direction', 'recorded_by', 'created_at')
    list_filter = ('direction', 'created_at')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'user__student_id')
    raw_id_fields = ('user', 'recorded_by')


from .models import LeaveRequest


@admin.register(LeaveRequest)
class LeaveRequestAdmin(admin.ModelAdmin):
    list_display = ('user', 'start_at', 'end_at', 'status', 'created_at')
    list_filter = ('status',)
    search_fields = ('user__username', 'user__student_id', 'reason')
