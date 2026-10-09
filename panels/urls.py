from django.urls import path

from . import views_cook as cook
from . import views_guard as guard
from . import views_maintenance as maintenance
from . import views_manager as manager

app_name = 'panels'

urlpatterns = [
    # ---- آشپز ----
    path('cook/', cook.dashboard, name='cook_dashboard'),
    path('cook/orders/', cook.orders, name='cook_orders'),
    path('cook/orders/<int:pk>/serve/', cook.serve_order, name='cook_serve'),
    path('cook/serve/', cook.serve_by_code, name='cook_serve_code'),
    path('cook/items/', cook.menu_items, name='cook_items'),
    path('cook/items/<int:pk>/toggle/', cook.toggle_item, name='cook_item_toggle'),
    path('cook/menu/', cook.weekly_menu, name='cook_menu'),

    # ---- تاسیسات ----
    path('maintenance/', maintenance.dashboard, name='maintenance_dashboard'),
    path('maintenance/tickets/', maintenance.tickets, name='maintenance_tickets'),

    # ---- گارد ----
    path('guard/', guard.dashboard, name='guard_dashboard'),
    path('guard/gate/', guard.gate, name='guard_gate'),
    path('guard/record/', guard.record, name='guard_record'),
    path('guard/outside/', guard.outside, name='guard_outside'),
    path('guard/logs/', guard.logs, name='guard_logs'),

    # ---- مدیریت ----
    path('manager/', manager.dashboard, name='manager_dashboard'),
    path('manager/users/', manager.users, name='manager_users'),
    path('manager/users/new/', manager.user_create, name='manager_user_create'),
    path('manager/users/<int:pk>/', manager.user_edit, name='manager_user_edit'),
    path('manager/users/<int:pk>/toggle/', manager.user_toggle_active, name='manager_user_toggle'),
    path('manager/students/import/', manager.students_import, name='manager_students_import'),
    path('manager/students/import/template/', manager.students_import_template, name='manager_students_import_template'),
    path('manager/students/import/upload/', manager.students_import_upload, name='manager_students_import_upload'),
    path('manager/backup/', manager.backup_page, name='manager_backup'),
    path('manager/backup/download/db/', manager.backup_download_db, name='manager_backup_db'),
    path('manager/backup/download/json/', manager.backup_download_json, name='manager_backup_json'),
    path('manager/backup/restore/', manager.backup_restore, name='manager_backup_restore'),
    # اتاق‌ها
    path('manager/rooms/', manager.rooms, name='manager_rooms'),
    path('manager/rooms/assign/', manager.room_assign, name='manager_room_assign'),
    # گزارش‌ها
    path('manager/reports/', manager.reports, name='manager_reports'),
    path('manager/reports/export/<str:kind>/', manager.report_export, name='manager_report_export'),
    # تنظیمات
    path('manager/settings/', manager.system_settings, name='manager_settings'),
    # مرخصی‌ها
    path('manager/leaves/', manager.leaves_manage, name='manager_leaves'),
    path('manager/leaves/<int:pk>/review/', manager.leave_review, name='manager_leave_review'),
]
