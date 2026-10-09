"""پنل آشپز: سفارش‌های امروز، تحویل غذا، مدیریت غذاها و منوی هفتگی."""
from datetime import date, timedelta

from django.contrib import messages
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.translation import gettext as _
from django.views.decorators.http import require_POST

from accounts.permissions import role_required
from cafeteria.models import MealItem, MealOrder, WeeklyMenu
from cafeteria.views import get_current_week_start
from .forms import MealItemForm

cook_only = role_required('cook')


def _parse_date(value, default):
    try:
        return date.fromisoformat(value)
    except (TypeError, ValueError):
        return default


def _menu_for(day, period=None):
    week_start = get_current_week_start(day)
    weekday = (day.weekday() + 2) % 7
    qs = WeeklyMenu.objects.filter(week_start=week_start, weekday=weekday)
    if period:
        return qs.filter(meal_period=period).first()
    # پیش‌فرض: ناهار، وگرنه اولین منوی روز
    return qs.filter(meal_period='lunch').first() or qs.first()


def _menus_for(day):
    week_start = get_current_week_start(day)
    weekday = (day.weekday() + 2) % 7
    return list(WeeklyMenu.objects.filter(week_start=week_start, weekday=weekday).order_by('meal_period'))


def _totals(menu):
    """تعداد سفارش هر غذا برای یک منو."""
    if not menu:
        return []
    return (MealOrder.objects.filter(menu=menu)
            .values('meal_item__name_fa')
            .annotate(total=Count('id'), served=Count('id', filter=Q(is_served=True)))
            .order_by('-total'))


@cook_only
def dashboard(request):
    today = timezone.localdate()
    tomorrow = today + timedelta(days=1)
    menus_today = _menus_for(today)
    menus_tomorrow = _menus_for(tomorrow)
    totals_today = []
    for m in menus_today:
        for row in _totals(m):
            row = dict(row)
            row['period'] = m.get_meal_period_display()
            totals_today.append(row)
    totals_tomorrow = []
    for m in menus_tomorrow:
        for row in _totals(m):
            row = dict(row)
            row['period'] = m.get_meal_period_display()
            totals_tomorrow.append(row)
    orders_today = MealOrder.objects.filter(menu__in=menus_today).count() if menus_today else 0
    served_today = MealOrder.objects.filter(menu__in=menus_today, is_served=True).count() if menus_today else 0
    return render(request, 'panels/cook/dashboard.html', {
        'today': today, 'tomorrow': tomorrow,
        'menu_today': menus_today[0] if menus_today else None,
        'menu_tomorrow': menus_tomorrow[0] if menus_tomorrow else None,
        'totals_today': totals_today,
        'totals_tomorrow': totals_tomorrow,
        'orders_today': orders_today,
        'served_today': served_today,
        'pending_today': orders_today - served_today,
    })


@cook_only
def orders(request):
    day = _parse_date(request.GET.get('date'), timezone.localdate())
    period = request.GET.get('period', '')
    menus = _menus_for(day)
    if period:
        menus = [m for m in menus if m.meal_period == period]
    menu_ids = [m.pk for m in menus]
    qs = MealOrder.objects.none()
    q = request.GET.get('q', '').strip()
    status = request.GET.get('status')
    if menu_ids:
        qs = MealOrder.objects.filter(menu_id__in=menu_ids).select_related('user', 'meal_item', 'menu')
        if q:
            qs = qs.filter(
                Q(user__first_name__icontains=q) | Q(user__last_name__icontains=q)
                | Q(user__student_id__icontains=q) | Q(user__username__icontains=q)
                | Q(receipt_code__icontains=q)
            )
        if status == 'served':
            qs = qs.filter(is_served=True)
        elif status == 'pending':
            qs = qs.filter(is_served=False)
    totals = []
    for m in menus:
        for row in _totals(m):
            row = dict(row)
            row['period'] = m.get_meal_period_display()
            totals.append(row)
    return render(request, 'panels/cook/orders.html', {
        'day': day, 'prev_day': day - timedelta(days=1), 'next_day': day + timedelta(days=1),
        'menu': menus[0] if menus else None, 'orders': qs, 'totals': totals,
        'q': q, 'status': status or '', 'period': period,
        'periods': [('breakfast', 'صبحانه'), ('lunch', 'ناهار'), ('dinner', 'شام')],
    })


@cook_only
@require_POST
def serve_order(request, pk):
    order = get_object_or_404(MealOrder, pk=pk)
    if order.is_served:
        order.is_served, order.served_at, order.served_by = False, None, None
    else:
        order.is_served, order.served_at, order.served_by = True, timezone.now(), request.user
    order.save(update_fields=['is_served', 'served_at', 'served_by'])
    return redirect(request.POST.get('next') or 'panels:cook_orders')


@cook_only
def menu_items(request):
    """لیست غذاها + افزودن/ویرایش."""
    edit_id = request.GET.get('edit')
    instance = get_object_or_404(MealItem, pk=edit_id) if edit_id else None
    if request.method == 'POST':
        form = MealItemForm(request.POST, instance=instance)
        if form.is_valid():
            form.save()
            messages.success(request, _('غذا ذخیره شد.'))
            return redirect('panels:cook_items')
    else:
        form = MealItemForm(instance=instance)
    return render(request, 'panels/cook/items.html', {
        'items': MealItem.objects.all(), 'form': form, 'editing': instance,
    })


@cook_only
@require_POST
def toggle_item(request, pk):
    item = get_object_or_404(MealItem, pk=pk)
    item.is_active = not item.is_active
    item.save(update_fields=['is_active'])
    return redirect('panels:cook_items')


@cook_only
def weekly_menu(request):
    """تعیین غذاهای هر روز و هر وعده (هفته جاری یا هفته بعد)."""
    from cafeteria.models import MealPeriod
    current = get_current_week_start()
    week_start = current + timedelta(days=7) if request.GET.get('week') == 'next' else current
    items = MealItem.objects.filter(is_active=True)
    periods = list(MealPeriod)

    if request.method == 'POST':
        for weekday, _label in WeeklyMenu.Weekday.choices:
            for period, _plabel in periods:
                key = f'day_{weekday}_{period}'
                chosen = request.POST.getlist(key)
                valid = items.filter(pk__in=chosen)
                menu = WeeklyMenu.objects.filter(
                    week_start=week_start, weekday=weekday, meal_period=period
                ).first()
                if menu is None and not valid:
                    continue
                if menu is None:
                    menu = WeeklyMenu.objects.create(
                        week_start=week_start, weekday=weekday, meal_period=period
                    )
                ordered_ids = set(menu.orders.values_list('meal_item_id', flat=True))
                menu.options.set(set(valid) | set(MealItem.objects.filter(pk__in=ordered_ids)))
        messages.success(request, _('منوی هفته ذخیره شد.'))
        return redirect(request.get_full_path())

    existing = {
        (m.weekday, m.meal_period): m
        for m in WeeklyMenu.objects.filter(week_start=week_start).prefetch_related('options')
    }
    days = []
    for weekday, label in WeeklyMenu.Weekday.choices:
        period_blocks = []
        for period, plabel in periods:
            menu = existing.get((weekday, period))
            selected = {o.pk for o in menu.options.all()} if menu else set()
            period_blocks.append({
                'period': period, 'label': plabel,
                'choices': [(i, i.pk in selected) for i in items],
            })
        days.append({
            'weekday': weekday, 'label': label,
            'date': week_start + timedelta(days=weekday),
            'periods': period_blocks,
        })
    return render(request, 'panels/cook/weekly_menu.html', {
        'days': days, 'week_start': week_start, 'is_next': week_start != current,
    })



@cook_only
def serve_by_code(request):
    """صفحه ثبت تحویل با وارد کردن کد فیش."""
    order = None
    lookup_code = ''
    if request.method == 'POST':
        action = request.POST.get('action', 'lookup')
        lookup_code = (request.POST.get('receipt_code') or '').strip().upper()

        if action == 'lookup':
            if not lookup_code:
                messages.error(request, _('کد فیش را وارد کنید.'))
            else:
                order = (MealOrder.objects
                         .filter(receipt_code__iexact=lookup_code)
                         .select_related('user', 'meal_item', 'menu')
                         .first())
                if order is None:
                    messages.error(request, _('سفارشی با کد «%(c)s» یافت نشد.') % {'c': lookup_code})
                elif order.is_served:
                    messages.warning(
                        request,
                        _('این فیش قبلاً تحویل شده است (%(name)s — %(meal)s).')
                        % {'name': order.user.display_name, 'meal': order.meal_item.name_fa},
                    )
                # اگر پیدا شد و تحویل نشده، در تمپلیت نمایش داده می‌شود

        elif action == 'confirm':
            pk = request.POST.get('order_id')
            order = get_object_or_404(
                MealOrder.objects.select_related('user', 'meal_item', 'menu'),
                pk=pk,
            )
            if order.is_served:
                messages.warning(request, _('این سفارش قبلاً تحویل شده بود.'))
            else:
                order.is_served = True
                order.served_at = timezone.now()
                order.served_by = request.user
                order.save(update_fields=['is_served', 'served_at', 'served_by'])
                messages.success(
                    request,
                    _('✓ تحویل ثبت شد: %(name)s — %(meal)s — کد %(code)s')
                    % {
                        'name': order.user.display_name,
                        'meal': order.meal_item.name_fa,
                        'code': order.receipt_code,
                    },
                )
                order = None  # پاک کردن فرم برای فیش بعدی
                lookup_code = ''

    # آخرین تحویل‌های امروز برای نمایش سریع
    today = timezone.localdate()
    recent_served = (
        MealOrder.objects.filter(is_served=True, served_at__date=today)
        .select_related('user', 'meal_item')
        .order_by('-served_at')[:12]
    )

    return render(request, 'panels/cook/serve_code.html', {
        'order': order,
        'lookup_code': lookup_code,
        'recent_served': recent_served,
    })
