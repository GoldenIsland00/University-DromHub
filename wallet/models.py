from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator
from decimal import Decimal


class Wallet(models.Model):
    """کیف پول هر کاربر"""
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='wallet',
        verbose_name=_('کاربر')
    )
    balance = models.DecimalField(
        _('موجودی'),
        max_digits=12,
        decimal_places=0,
        default=Decimal('0'),
        validators=[MinValueValidator(Decimal('0'))]
    )
    updated_at = models.DateTimeField(_('آخرین بروزرسانی'), auto_now=True)

    class Meta:
        verbose_name = _('کیف پول')
        verbose_name_plural = _('کیف پول‌ها')

    def __str__(self):
        return f"{self.user} - {self.balance} تومان"

    def can_afford(self, amount):
        return self.balance >= amount

    def deposit(self, amount, description='', performed_by=None):
        amount = Decimal(amount)
        if amount <= 0:
            raise ValueError('Amount must be positive')
        self.balance += amount
        self.save(update_fields=['balance', 'updated_at'])
        Transaction.objects.create(
            wallet=self,
            amount=amount,
            transaction_type=Transaction.Type.CHARGE,
            description=description or 'شارژ حساب',
            performed_by=performed_by
        )
        return self.balance

    def withdraw(self, amount, description='', transaction_type=None):
        amount = Decimal(amount)
        if amount <= 0:
            raise ValueError('Amount must be positive')
        if not self.can_afford(amount):
            raise ValueError('موجودی کافی نیست')
        self.balance -= amount
        self.save(update_fields=['balance', 'updated_at'])
        Transaction.objects.create(
            wallet=self,
            amount=-amount,
            transaction_type=transaction_type or Transaction.Type.MEAL,
            description=description or 'برداشت'
        )
        return self.balance


class Transaction(models.Model):
    class Type(models.TextChoices):
        CHARGE = 'charge', _('شارژ')
        MEAL = 'meal', _('خرید غذا')
        REFUND = 'refund', _('بازگشت وجه')
        ADJUSTMENT = 'adjustment', _('تعدیل توسط مدیر')

    wallet = models.ForeignKey(
        Wallet,
        on_delete=models.CASCADE,
        related_name='transactions',
        verbose_name=_('کیف پول')
    )
    amount = models.DecimalField(
        _('مبلغ'),
        max_digits=12,
        decimal_places=0
    )  # positive = charge, negative = spend
    transaction_type = models.CharField(
        _('نوع'),
        max_length=20,
        choices=Type.choices
    )
    description = models.CharField(_('توضیحات'), max_length=255, blank=True)
    performed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='performed_transactions',
        verbose_name=_('انجام‌دهنده')
    )
    created_at = models.DateTimeField(_('تاریخ'), auto_now_add=True)
    balance_after = models.DecimalField(
        _('موجودی بعد از تراکنش'),
        max_digits=12,
        decimal_places=0,
        null=True,
        blank=True
    )

    class Meta:
        verbose_name = _('تراکنش')
        verbose_name_plural = _('تراکنش‌ها')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_transaction_type_display()} - {self.amount}"

    def save(self, *args, **kwargs):
        if self.balance_after is None and self.wallet_id:
            self.balance_after = self.wallet.balance
        super().save(*args, **kwargs)
