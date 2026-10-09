from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """Custom user model for students, staff and admins."""

    class Gender(models.TextChoices):
        MALE = 'male', _('برادران / Brothers')
        FEMALE = 'female', _('خواهران / Sisters')

    class Role(models.TextChoices):
        STUDENT = 'student', _('دانشجو')
        COOK = 'cook', _('آشپز')
        MAINTENANCE = 'maintenance', _('تاسیسات')
        GUARD = 'guard', _('گارد / حراست')
        MANAGER = 'manager', _('مدیریت')
        ADMIN = 'admin', _('مدیر سیستم')

    # نقش‌هایی که پنل مخصوص خودشان را دارند (به‌جز دانشجو)
    STAFF_ROLES = ('cook', 'maintenance', 'guard', 'manager', 'admin')

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
        """مدیر سیستم (بالاترین سطح)."""
        return self.role == self.Role.ADMIN or self.is_superuser

    @property
    def is_manager_level(self):
        """مدیریت یا مدیر سیستم: دسترسی به پنل مدیریت و مدیریت کاربران."""
        return self.is_admin_user or self.role == self.Role.MANAGER

    @property
    def is_cook(self):
        return self.role == self.Role.COOK

    @property
    def is_maintenance(self):
        return self.role == self.Role.MAINTENANCE

    @property
    def is_guard(self):
        return self.role == self.Role.GUARD

    @property
    def is_staff_member(self):
        """هر کاربری که دانشجو نیست."""
        return self.is_superuser or self.role in self.STAFF_ROLES

    @property
    def panel_url_name(self):
        """نام URL داشبورد پنل مخصوص این نقش."""
        if self.is_manager_level:
            return 'panels:manager_dashboard'
        return {
            self.Role.COOK: 'panels:cook_dashboard',
            self.Role.MAINTENANCE: 'panels:maintenance_dashboard',
            self.Role.GUARD: 'panels:guard_dashboard',
        }.get(self.role, 'dashboard')

    @property
    def display_name(self):
        return self.get_full_name() or self.username

    def get_initials(self):
        name = self.get_full_name() or self.username
        parts = name.split()
        if len(parts) >= 2:
            return (parts[0][0] + parts[1][0]).upper()
        return name[:2].upper()
