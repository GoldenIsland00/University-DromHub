from django.contrib import admin
from .models import Wallet, Transaction


class TransactionInline(admin.TabularInline):
    model = Transaction
    extra = 0
    readonly_fields = ('amount', 'transaction_type', 'description', 'created_at', 'balance_after')
    can_delete = False


@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ('user', 'balance', 'updated_at')
    search_fields = ('user__username', 'user__first_name', 'user__student_id')
    readonly_fields = ('updated_at',)
    inlines = [TransactionInline]
    actions = ['add_100k', 'add_50k']

    @admin.action(description='شارژ ۱۰۰,۰۰۰ تومان')
    def add_100k(self, request, queryset):
        for w in queryset:
            w.deposit(100000, description='شارژ توسط مدیر', performed_by=request.user)

    @admin.action(description='شارژ ۵۰,۰۰۰ تومان')
    def add_50k(self, request, queryset):
        for w in queryset:
            w.deposit(50000, description='شارژ توسط مدیر', performed_by=request.user)


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('wallet', 'transaction_type', 'amount', 'description', 'created_at')
    list_filter = ('transaction_type', 'created_at')
    search_fields = ('wallet__user__username', 'description')
    readonly_fields = ('created_at', 'balance_after')
