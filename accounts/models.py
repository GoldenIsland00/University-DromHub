from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """Custom user model for students, staff and admins."""

    class Gender(models.TextChoices):
        MALE = 'male', _('برادران / Brothers')
        FEMALE = 'female', _('خواهران / Sisters')

    class Role(models.TextChoices):
        STUDENT = 'student', _('دانشجو / Student')
        STAFF = 'staff', _('کارمند / Staff')
        ADMIN = 'admin', _('مدیر / Admin')

    student_id = models.CharField(
        _('شماره دانشجویی'),
        max_length=20,
        unique=True,
        null=True,
        blank=True,
        help_text=_('برای دانشجویان الزامی است')
    )
    phone = models.CharField(_('شماره موبایل'), max_length=15, blank=True)
    gender = models.CharField(
        _('بخش خوابگاه'),
        max_length=10,
        choices=Gender.choices,
        blank=True,
        null=True
    )
    role = models.CharField(
        _('نقش'),
        max_length=20,
        choices=Role.choices,
        default=Role.STUDENT
    )
    avatar = models.ImageField(
        _('تصویر پروفایل'),
        upload_to='avatars/',
        blank=True,
        null=True
    )
    is_active_student = models.BooleanField(_('فعال'), default=True)

    class Meta:
        verbose_name = _('کاربر')
        verbose_name_plural = _('کاربران')
        ordering = ['-date_joined']

    def __str__(self):
        return self.get_full_name() or self.username

    @property
    def is_student(self):
        return self.role == self.Role.STUDENT

    @property
    def is_admin_user(self):
        return self.role == self.Role.ADMIN or self.is_superuser

    @property
    def display_name(self):
        return self.get_full_name() or self.username

    def get_initials(self):
        name = self.get_full_name() or self.username
        parts = name.split()
        if len(parts) >= 2:
            return (parts[0][0] + parts[1][0]).upper()
        return name[:2].upper()
