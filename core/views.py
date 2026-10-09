from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils import timezone

from accounts.models import User
from cafeteria.models import MealOrder, WeeklyMenu
from cafeteria.views import get_current_week_start, get_today_weekday
from dormitory.models import Room
from tickets.models import Ticket


def home_view(request):
    today = timezone.localdate()
    stats = {
        'students': User.objects.filter(role=User.Role.STUDENT).count(),
        'rooms': Room.objects.filter(is_active=True).count(),
        'open_tickets': Ticket.objects.filter(status__in=['open', 'in_progress']).count(),
        'today_orders': MealOrder.objects.filter(
            menu__week_start=get_current_week_start(today),
            menu__weekday=get_today_weekday(today),
        ).count(),
    }
    return render(request, 'core/home.html', {'stats': stats})


@login_required
def dashboard_view(request):
    """دانشجو داشبورد خودش را می‌بیند؛ بقیه نقش‌ها به پنل مخصوص خودشان می‌روند."""
    user = request.user
    if not user.is_student:
        return redirect(user.panel_url_name)

    context = {
        'recent_tickets': user.tickets.all()[:5],
        'roommates': [],
        'today_meal': None,
    }
    if hasattr(user, 'bed') and user.bed:
        context['roommates'] = user.bed.room.beds.select_related('occupant').order_by('number')

    today = timezone.localdate()
    menu = WeeklyMenu.objects.filter(
        week_start=get_current_week_start(today), weekday=get_today_weekday(today)
    ).first()
    if menu:
        context['today_meal'] = MealOrder.objects.filter(user=user, menu=menu).select_related('meal_item').first()
    return render(request, 'core/dashboard.html', context)


@login_required
def admin_dashboard(request):
    """آدرس قدیمی /admin-panel/ → پنل مدیریت جدید."""
    return redirect('panels:manager_dashboard')
