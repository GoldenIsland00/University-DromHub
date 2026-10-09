from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator
from datetime import timedelta
from decimal import Decimal
import secrets


class MealPeriod(models.TextChoices):
    BREAKFAST = 'breakfast', _('صبحانه')
    LUNCH = 'lunch', _('ناهار')
    DINNER = 'dinner', _('شام')


class MealItem(models.Model):
    """آیتم غذایی موجود در منو"""
    name_fa = models.CharField(_('نام فارسی'), max_length=100)
    name_en = models.CharField(_('نام انگلیسی'), max_length=100, blank=True)
    price = models.DecimalField(
        _('قیمت (تومان)'),
        max_digits=10,
        decimal_places=0,
        validators=[MinValueValidator(Decimal('0'))]
    )
    is_active = models.BooleanField(_('فعال'), default=True)
    description = models.TextField(_('توضیحات'), blank=True)

    class Meta:
        verbose_name = _('آیتم غذایی')
        verbose_name_plural = _('آیتم‌های غذایی')
        ordering = ['name_fa']

    def __str__(self):
        return f"{self.name_fa} ({self.price} تومان)"

    def get_name(self, lang='fa'):
        if lang == 'en' and self.name_en:
            return self.name_en
        return self.name_fa


class WeeklyMenu(models.Model):
    """منوی یک وعده از یک روز هفته"""
    class Weekday(models.IntegerChoices):
        SATURDAY = 0, _('شنبه')
        SUNDAY = 1, _('یکشنبه')
        MONDAY = 2, _('دوشنبه')
        TUESDAY = 3, _('سه‌شنبه')
        WEDNESDAY = 4, _('چهارشنبه')
        THURSDAY = 5, _('پنج‌شنبه')
        FRIDAY = 6, _('جمعه')

    week_start = models.DateField(_('شروع هفته (شنبه)'))
    weekday = models.PositiveSmallIntegerField(
        _('روز هفته'),
        choices=Weekday.choices
    )
    meal_period = models.CharField(
        _('وعده'),
        max_length=20,
        choices=MealPeriod.choices,
        default=MealPeriod.LUNCH,
        db_index=True,
    )
    options = models.ManyToManyField(
        MealItem,
        related_name='menus',
        verbose_name=_('گزینه‌های غذایی')
    )

    class Meta:
        verbose_name = _('منوی روزانه')
        verbose_name_plural = _('منوی هفتگی')
        unique_together = ['week_start', 'weekday', 'meal_period']
        ordering = ['week_start', 'weekday', 'meal_period']

    def __str__(self):
        return f"{self.get_weekday_display()} — {self.get_meal_period_display()} — {self.week_start}"

    @property
    def date(self):
        return self.week_start + timedelta(days=self.weekday)


class MealOrder(models.Model):
    """سفارش غذای دانشجو برای یک وعده"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='meal_orders',
        verbose_name=_('کاربر')
    )
    menu = models.ForeignKey(
        WeeklyMenu,
        on_delete=models.CASCADE,
        related_name='orders',
        verbose_name=_('منو')
    )
    meal_item = models.ForeignKey(
        MealItem,
        on_delete=models.PROTECT,
        related_name='orders',
        verbose_name=_('غذا')
    )
    price_at_order = models.DecimalField(
        _('قیمت در زمان سفارش'),
        max_digits=10,
        decimal_places=0
    )
    created_at = models.DateTimeField(_('تاریخ سفارش'), auto_now_add=True)
    is_served = models.BooleanField(_('تحویل داده شد'), default=False)
    served_at = models.DateTimeField(_('زمان تحویل'), null=True, blank=True)
    served_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='served_orders',
        verbose_name=_('تحویل‌دهنده')
    )
    receipt_code = models.CharField(
        _('کد فیش'),
        max_length=12,
        unique=True,
        db_index=True,
        blank=True,
        help_text=_('کد یکتای هر وعده برای تحویل در سلف')
    )

    class Meta:
        verbose_name = _('سفارش غذا')
        verbose_name_plural = _('سفارش‌های غذا')
        unique_together = ['user', 'menu']
        ordering = ['-created_at']

    @staticmethod
    def generate_receipt_code():
        alphabet = 'ABCDEFGHJKMNPQRSTUVWXYZ23456789'
        for _ in range(50):
            code = ''.join(secrets.choice(alphabet) for _ in range(6))
            if not MealOrder.objects.filter(receipt_code=code).exists():
                return code
        return secrets.token_hex(4).upper()

    def save(self, *args, **kwargs):
        if not self.receipt_code:
            self.receipt_code = self.generate_receipt_code()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user} - {self.meal_item} ({self.menu}) [{self.receipt_code}]"

    @property
    def meal_period(self):
        return self.menu.meal_period
