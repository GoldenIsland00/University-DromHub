from django.contrib import admin
from .models import Ticket, TicketReply


class TicketReplyInline(admin.TabularInline):
    model = TicketReply
    extra = 0
    readonly_fields = ('user', 'created_at', 'is_staff_reply')


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ('id', 'subject', 'user', 'category', 'priority', 'status', 'created_at')
    list_filter = ('status', 'priority', 'category', 'created_at')
    search_fields = ('subject', 'user__username', 'user__first_name', 'description')
    list_editable = ('status', 'priority')
    inlines = [TicketReplyInline]
    raw_id_fields = ('user', 'room')


@admin.register(TicketReply)
class TicketReplyAdmin(admin.ModelAdmin):
    list_display = ('ticket', 'user', 'is_staff_reply', 'created_at')
    list_filter = ('is_staff_reply',)
