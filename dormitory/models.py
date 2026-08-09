from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class Building(models.Model):
    """ساختمان خوابگاه"""
    class Section(models.TextChoices):
        MALE = 'male', _('برادران')
        FEMALE = 'female', _('خواهران')

    name = models.CharField(_('نام ساختمان'), max_length=100)
    section = models.CharField(_('بخش'), max_length=10, choices=Section.choices)
    floors = models.PositiveSmallIntegerField(_('تعداد طبقات'), default=4)
    description = models.TextField(_('توضیحات'), blank=True)

    class Meta:
        verbose_name = _('ساختمان')
        verbose_name_plural = _('ساختمان‌ها')

    def __str__(self):
        return f"{self.name} ({self.get_section_display()})"


class Room(models.Model):
    """اتاق خوابگاه"""
    building = models.ForeignKey(
        Building,
        on_delete=models.CASCADE,
        related_name='rooms',
        verbose_name=_('ساختمان')
    )
    number = models.CharField(_('شماره اتاق'), max_length=20)
    floor = models.PositiveSmallIntegerField(_('طبقه'))
    capacity = models.PositiveSmallIntegerField(_('ظرفیت'), default=4)
    is_active = models.BooleanField(_('فعال'), default=True)

    class Meta:
        verbose_name = _('اتاق')
        verbose_name_plural = _('اتاق‌ها')
        unique_together = ['building', 'number']
        ordering = ['building', 'floor', 'number']

    def __str__(self):
        return f"{self.building.name} - {self.number}"

    @property
    def occupied_count(self):
        return self.beds.filter(occupant__isnull=False).count()

    @property
    def is_full(self):
        return self.occupied_count >= self.capacity

    @property
    def section(self):
        return self.building.section


class Bed(models.Model):
    """تخت داخل اتاق"""
    room = models.ForeignKey(
        Room,
        on_delete=models.CASCADE,
        related_name='beds',
        verbose_name=_('اتاق')
    )
    number = models.PositiveSmallIntegerField(_('شماره تخت'))
    occupant = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='bed',
        verbose_name=_('ساکن')
    )

    class Meta:
        verbose_name = _('تخت')
        verbose_name_plural = _('تخت‌ها')
        unique_together = ['room', 'number']
        ordering = ['room', 'number']

    def __str__(self):
        status = self.occupant.display_name if self.occupant else 'خالی'
        return f"اتاق {self.room.number} - تخت {self.number} ({status})"
