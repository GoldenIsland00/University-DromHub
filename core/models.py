"""تنظیمات سیستم و اعلان‌های درون‌برنامه‌ای."""
from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from decimal import Decimal


class SystemSettings(models.Model):
    """تنظیمات سراسری — فقط یک ردیف (pk=1)."""
    site_name = models.CharField(_('نام سامانه'), max_length=120, default='سامانه خوابگاه و سلف')
    order_cutoff_hour = models.PositiveSmallIntegerField(
        _('ساعت قطع سفارش همان روز'),
        default=10,
        help_text=_('بعد از این ساعت (۰–۲۳) نمی‌توان برای امروز سفارش داد'),
    )
    low_balance_threshold = models.DecimalField(
        _('آستانه هشدار موجودی کم'),
        max_digits=12, decimal_places=0, default=Decimal('50000'),
    )
    allow_student_charge = models.BooleanField(
        _('اجازه شارژ آنلاین توسط دانشجو'), default=True,
    )
    mock_payment_enabled = models.BooleanField(
        _('درگاه ساختگی (دمو) فعال باشد'), default=True,
    )
    breakfast_enabled = models.BooleanField(_('فعال بودن صبحانه'), default=True)
    lunch_enabled = models.BooleanField(_('فعال بودن ناهار'), default=True)
    dinner_enabled = models.BooleanField(_('فعال بودن شام'), default=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('تنظیمات سیستم')
        verbose_name_plural = _('تنظیمات سیستم')

    def __str__(self):
        return self.site_name

    @classmethod
    def get(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class Notification(models.Model):
    class Kind(models.TextChoices):
        INFO = 'info', _('اطلاع')
        SUCCESS = 'success', _('موفق')
        WARNING = 'warning', _('هشدار')
        TICKET = 'ticket', _('تیکت')
        MEAL = 'meal', _('غذا')
        WALLET = 'wallet', _('کیف پول')
        LEAVE = 'leave', _('مرخصی')

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='notifications', verbose_name=_('کاربر'),
    )
    kind = models.CharField(max_length=20, choices=Kind.choices, default=Kind.INFO)
    title = models.CharField(_('عنوان'), max_length=200)
    body = models.TextField(_('متن'), blank=True)
    link = models.CharField(_('لینک'), max_length=300, blank=True)
    is_read = models.BooleanField(_('خوانده شده'), default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('اعلان')
        verbose_name_plural = _('اعلان‌ها')
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user} — {self.title}'

    @classmethod
    def notify(cls, user, title, body='', kind='info', link=''):
        if user is None:
            return None
        return cls.objects.create(user=user, title=title, body=body, kind=kind, link=link)
