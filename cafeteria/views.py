from datetime import timedelta
from decimal import Decimal

from django.contrib import messages
from django.db import transaction as db_transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.translation import gettext as _
from django.views.decorators.http import require_POST
from django.urls import reverse

from accounts.permissions import student_required
from core.models import SystemSettings, Notification
from wallet.models import Transaction, Wallet
from .models import MealOrder, WeeklyMenu, MealPeriod


def get_current_week_start(today=None):
    today = today or timezone.localdate()
    days_since_sat = (today.weekday() + 2) % 7
    return today - timedelta(days=days_since_sat)


def get_today_weekday(today=None):
    today = today or timezone.localdate()
    return (today.weekday() + 2) % 7


def enabled_periods():
    cfg = SystemSettings.get()
    periods = []
    if cfg.breakfast_enabled:
        periods.append(MealPeriod.BREAKFAST)
    if cfg.lunch_enabled:
        periods.append(MealPeriod.LUNCH)
    if cfg.dinner_enabled:
        periods.append(MealPeriod.DINNER)
    return periods or [MealPeriod.LUNCH]


@student_required
def meal_order_view(request):
    today = timezone.localdate()
    current_start = get_current_week_start(today)
    show_next = request.GET.get('week') == 'next'
    week_start = current_start + timedelta(days=7) if show_next else current_start
    period_filter = request.GET.get('period', '')
    periods = enabled_periods()

    menus_qs = WeeklyMenu.objects.filter(week_start=week_start).prefetch_related('options').order_by('weekday', 'meal_period')
    if period_filter in periods:
        menus_qs = menus_qs.filter(meal_period=period_filter)
    else:
        menus_qs = menus_qs.filter(meal_period__in=periods)

    menus = list(menus_qs)
    cfg = SystemSettings.get()
    now = timezone.localtime()

    for menu in menus:
        menu.items = [i for i in menu.options.all() if i.is_active]
        menu.is_past = menu.date < today
        if menu.date == today and now.hour >= cfg.order_cutoff_hour:
            menu.is_past = True
        menu.can_cancel = menu.date > today

    existing = {
        o.menu_id: o for o in MealOrder.objects.filter(
            user=request.user, menu__week_start=week_start
        ).select_related('meal_item', 'menu')
    }
    for menu in menus:
        menu.order = existing.get(menu.pk)

    wallet = request.user.wallet

    if request.method == 'POST':
        redirect_url = reverse('cafeteria:meals')
        if show_next:
            redirect_url += '?week=next'
        if period_filter:
            redirect_url += ('&' if '?' in redirect_url else '?') + f'period={period_filter}'

        selected = []
        total_cost = Decimal('0')
        for menu in menus:
            item_id = request.POST.get(f'menu_{menu.pk}')
            if not item_id or menu.order or menu.is_past:
                continue
            item = next((i for i in menu.items if str(i.pk) == item_id), None)
            if item is None:
                messages.error(request, _('غذای انتخاب‌شده برای این وعده معتبر نیست.'))
                return redirect(redirect_url)
            selected.append((menu, item))
            total_cost += item.price

        if not selected:
            messages.info(request, _('هیچ وعده جدیدی انتخاب نشده بود.'))
            return redirect(redirect_url)

        try:
            with db_transaction.atomic():
                wallet = Wallet.objects.select_for_update().get(pk=wallet.pk)
                if not wallet.can_afford(total_cost):
                    messages.error(
                        request,
                        _('موجودی کیف پول کافی نیست. مبلغ لازم: %(cost)s تومان') % {'cost': f'{total_cost:,.0f}'}
                    )
                    return redirect(redirect_url)
                for menu, item in selected:
                    MealOrder.objects.create(
                        user=request.user, menu=menu, meal_item=item,
                        price_at_order=item.price,
                    )
                    wallet.withdraw(
                        item.price,
                        description=f'{item.name_fa} - {menu.get_meal_period_display()} - {menu.get_weekday_display()} {menu.date}',
                        transaction_type=Transaction.Type.MEAL,
                    )
                # هشدار موجودی کم
                thr = cfg.low_balance_threshold
                if wallet.balance < thr:
                    Notification.notify(
                        request.user, _('موجودی کیف پول کم است'),
                        _('موجودی شما %(b)s تومان است.') % {'b': f'{wallet.balance:,.0f}'},
                        kind='wallet', link='/wallet/',
                    )
        except Exception:
            messages.error(request, _('ثبت سفارش با خطا مواجه شد. دوباره تلاش کنید.'))
            return redirect(redirect_url)

        messages.success(
            request,
            _('%(n)s وعده ثبت و مبلغ %(cost)s تومان از کیف پول کسر شد.') % {
                'n': len(selected), 'cost': f'{total_cost:,.0f}'}
        )
        return redirect(redirect_url)

    history = MealOrder.objects.filter(user=request.user).select_related('meal_item', 'menu')[:20]
    return render(request, 'cafeteria/meals.html', {
        'menus': menus,
        'week_start': week_start,
        'show_next': show_next,
        'balance': wallet.balance,
        'week_total': sum((o.price_at_order for o in existing.values()), Decimal('0')),
        'history': history,
        'periods': [(p, MealPeriod(p).label) for p in periods],
        'period_filter': period_filter,
        'cutoff_hour': cfg.order_cutoff_hour,
    })


@student_required
@require_POST
def cancel_order_view(request, pk):
    order = get_object_or_404(MealOrder.objects.select_related('menu', 'meal_item'), pk=pk, user=request.user)
    if order.is_served or order.menu.date <= timezone.localdate():
        messages.error(request, _('این سفارش دیگر قابل لغو نیست.'))
        return redirect('cafeteria:meals')
    with db_transaction.atomic():
        wallet = Wallet.objects.select_for_update().get(user=request.user)
        wallet.deposit(
            order.price_at_order,
            description=_('بازگشت وجه لغو سفارش %(code)s') % {'code': order.receipt_code},
            transaction_type=Transaction.Type.REFUND,
        )
        order.delete()
    messages.success(request, _('سفارش لغو و مبلغ به کیف پول بازگشت.'))
    return redirect('cafeteria:meals')


@student_required
def receipt_print(request, pk):
    """صفحه چاپ فیش با QR."""
    order = get_object_or_404(
        MealOrder.objects.select_related('meal_item', 'menu', 'user'),
        pk=pk, user=request.user,
    )
    return render(request, 'cafeteria/receipt_print.html', {'order': order})
