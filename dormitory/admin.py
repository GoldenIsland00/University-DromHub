from django.contrib import admin
from .models import Building, Room, Bed


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
