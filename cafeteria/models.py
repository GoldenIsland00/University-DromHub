from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator
from decimal import Decimal


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
    """منوی یک روز از هفته"""
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
    options = models.ManyToManyField(
        MealItem,
        related_name='menus',
        verbose_name=_('گزینه‌های غذایی')
    )

    class Meta:
        verbose_name = _('منوی روزانه')
        verbose_name_plural = _('منوی هفتگی')
        unique_together = ['week_start', 'weekday']
        ordering = ['week_start', 'weekday']

    def __str__(self):
        return f"{self.get_weekday_display()} - {self.week_start}"


class MealOrder(models.Model):
    """سفارش غذای دانشجو برای یک روز"""
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

    class Meta:
        verbose_name = _('سفارش غذا')
        verbose_name_plural = _('سفارش‌های غذا')
        unique_together = ['user', 'menu']  # one meal per day per user
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user} - {self.meal_item} ({self.menu})"
