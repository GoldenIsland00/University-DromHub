from django.contrib import admin
from .models import MealItem, WeeklyMenu, MealOrder


@admin.register(MealItem)
class MealItemAdmin(admin.ModelAdmin):
    list_display = ('name_fa', 'name_en', 'price', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name_fa', 'name_en')
    list_editable = ('price', 'is_active')


@admin.register(WeeklyMenu)
class WeeklyMenuAdmin(admin.ModelAdmin):
    list_display = ('week_start', 'weekday', 'meal_period', 'get_weekday_display')
    list_filter = ('week_start', 'weekday', 'meal_period')
    filter_horizontal = ('options',)


@admin.register(MealOrder)
class MealOrderAdmin(admin.ModelAdmin):
    list_display = ('receipt_code', 'user', 'menu', 'meal_item', 'price_at_order', 'is_served', 'created_at')
    list_filter = ('menu__week_start', 'is_served', 'created_at')
    search_fields = ('receipt_code', 'user__username', 'user__first_name', 'user__student_id', 'meal_item__name_fa')
    raw_id_fields = ('user', 'menu', 'meal_item')
