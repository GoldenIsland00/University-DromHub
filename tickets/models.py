from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class Ticket(models.Model):
    class Category(models.TextChoices):
        FACILITY = 'facility', _('تسهیلات اتاق')
        ELECTRIC = 'electric', _('برق و نور')
        PLUMBING = 'plumbing', _('لوله‌کشی')
        CLEANING = 'cleaning', _('نظافت')
        OTHER = 'other', _('سایر')

    class Priority(models.TextChoices):
        LOW = 'low', _('کم')
        MEDIUM = 'medium', _('متوسط')
        HIGH = 'high', _('بالا')
        URGENT = 'urgent', _('فوری')

    class Status(models.TextChoices):
        OPEN = 'open', _('باز')
        IN_PROGRESS = 'in_progress', _('در حال بررسی')
        RESOLVED = 'resolved', _('حل شده')
        CLOSED = 'closed', _('بسته')

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='tickets',
        verbose_name=_('کاربر')
    )
    subject = models.CharField(_('موضوع'), max_length=200)
    category = models.CharField(
        _('دسته‌بندی'),
        max_length=20,
        choices=Category.choices,
        default=Category.OTHER
    )
    priority = models.CharField(
        _('اولویت'),
        max_length=20,
        choices=Priority.choices,
        default=Priority.MEDIUM
    )
    status = models.CharField(
        _('وضعیت'),
        max_length=20,
        choices=Status.choices,
        default=Status.OPEN
    )
    description = models.TextField(_('توضیحات'))
    attachment = models.ImageField(
        _('پیوست'),
        upload_to='tickets/',
        blank=True,
        null=True
    )
    room = models.ForeignKey(
        'dormitory.Room',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tickets',
        verbose_name=_('اتاق')
    )
    created_at = models.DateTimeField(_('تاریخ ایجاد'), auto_now_add=True)
    updated_at = models.DateTimeField(_('آخرین بروزرسانی'), auto_now=True)

    class Meta:
        verbose_name = _('تیکت')
        verbose_name_plural = _('تیکت‌ها')
        ordering = ['-created_at']

    def __str__(self):
        return f"#{self.pk} - {self.subject}"


class TicketReply(models.Model):
    ticket = models.ForeignKey(
        Ticket,
        on_delete=models.CASCADE,
        related_name='replies',
        verbose_name=_('تیکت')
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='ticket_replies',
        verbose_name=_('کاربر')
    )
    message = models.TextField(_('پیام'))
    is_staff_reply = models.BooleanField(_('پاسخ کارمند/مدیر'), default=False)
    created_at = models.DateTimeField(_('تاریخ'), auto_now_add=True)

    class Meta:
        verbose_name = _('پاسخ تیکت')
        verbose_name_plural = _('پاسخ‌های تیکت')
        ordering = ['created_at']

    def __str__(self):
        return f"Reply to #{self.ticket_id} by {self.user}"
