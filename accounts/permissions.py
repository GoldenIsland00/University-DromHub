"""
کنترل سطح دسترسی بر اساس نقش کاربر.

استفاده:
    @role_required('cook')                 # فقط آشپز (و مدیریت/مدیر سیستم)
    @role_required('guard', 'maintenance') # هر کدام از این دو
    @student_required                      # فقط دانشجو
"""
from functools import wraps

from django.contrib import messages
from django.contrib.auth.views import redirect_to_login
from django.shortcuts import redirect
from django.utils.translation import gettext as _


def role_required(*roles, allow_managers=True):
    """کاربر باید یکی از نقش‌های داده‌شده را داشته باشد.

    مدیریت و مدیر سیستم به‌صورت پیش‌فرض به همه پنل‌ها دسترسی دارند
    (با allow_managers=False می‌شود غیرفعالش کرد).
    """
    def decorator(view):
        @wraps(view)
        def wrapper(request, *args, **kwargs):
            user = request.user
            if not user.is_authenticated:
                return redirect_to_login(request.get_full_path())
            allowed = user.role in roles or (allow_managers and user.is_manager_level)
            if not allowed:
                messages.error(request, _('شما به این بخش دسترسی ندارید.'))
                return redirect(user.panel_url_name)
            return view(request, *args, **kwargs)
        return wrapper
    return decorator


def manager_required(view):
    """فقط مدیریت و مدیر سیستم."""
    return role_required(allow_managers=True)(view)


def student_required(view):
    """صفحات مخصوص دانشجو (سفارش غذا، کیف پول، اتاق من)."""
    @wraps(view)
    def wrapper(request, *args, **kwargs):
        user = request.user
        if not user.is_authenticated:
            return redirect_to_login(request.get_full_path())
        if not user.is_student:
            messages.info(request, _('این بخش مخصوص دانشجویان است.'))
            return redirect(user.panel_url_name)
        return view(request, *args, **kwargs)
    return wrapper
