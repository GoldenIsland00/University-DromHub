from datetime import date
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render
from accounts.models import User
from dormitory.models import Room
from tickets.models import Ticket
from cafeteria.models import MealOrder, WeeklyMenu
from cafeteria.views import get_current_week_start


def home_view(request):
    stats = {
        'students': User.objects.filter(role=User.Role.STUDENT).count(),
        'rooms': Room.objects.filter(is_active=True).count(),
        'open_tickets': Ticket.objects.filter(status__in=['open', 'in_progress']).count(),
        'today_orders': MealOrder.objects.filter(created_at__date=date.today()).count(),
    }
    return render(request, 'core/home.html', {'stats': stats})


@login_required
def dashboard_view(request):
    user = request.user
    context = {
        'recent_tickets': user.tickets.all()[:5],
        'roommates': [],
        'today_meal': None,
    }
    if hasattr(user, 'bed') and user.bed:
        room = user.bed.room
        context['roommates'] = room.beds.select_related('occupant').order_by('number')

    week_start = get_current_week_start()
    today_weekday = (date.today().weekday() + 2) % 7
    try:
        menu = WeeklyMenu.objects.get(week_start=week_start, weekday=today_weekday)
        order = MealOrder.objects.filter(user=user, menu=menu).select_related('meal_item').first()
        context['today_meal'] = order
    except WeeklyMenu.DoesNotExist:
        pass
    return render(request, 'core/dashboard.html', context)


def is_admin(user):
    return user.is_authenticated and (getattr(user, 'is_admin_user', False) or user.is_superuser or user.is_staff)


@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    context = {
        'total_users': User.objects.count(),
        'total_rooms': Room.objects.count(),
        'open_tickets': Ticket.objects.filter(status__in=['open', 'in_progress']).count(),
        'today_orders': MealOrder.objects.filter(created_at__date=date.today()).count(),
        'recent_tickets': Ticket.objects.filter(status='open').select_related('user')[:5],
        'male_rooms': Room.objects.filter(building__section='male').count(),
        'female_rooms': Room.objects.filter(building__section='female').count(),
        'male_students': User.objects.filter(gender='male', role='student').count(),
        'female_students': User.objects.filter(gender='female', role='student').count(),
    }
    return render(request, 'core/admin_dashboard.html', context)
