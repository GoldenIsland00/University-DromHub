from datetime import date, timedelta
from decimal import Decimal
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect
from django.utils.translation import gettext as _
from django.db import transaction as db_transaction
from .models import WeeklyMenu, MealOrder, MealItem
from wallet.models import Transaction


def get_current_week_start():
    today = date.today()
    # Saturday as start of week (Iranian)
    days_since_sat = (today.weekday() + 2) % 7  # Python Mon=0 ... adjust to Sat=0
    return today - timedelta(days=days_since_sat)


@login_required
def meal_order_view(request):
    week_start = get_current_week_start()
    menus = WeeklyMenu.objects.filter(week_start=week_start).prefetch_related('options').order_by('weekday')

    # Existing orders of this user for the week
    existing = {
        o.menu_id: o for o in MealOrder.objects.filter(
            user=request.user,
            menu__week_start=week_start
        ).select_related('meal_item')
    }

    if request.method == 'POST':
        total_cost = Decimal('0')
        orders_to_create = []
        try:
            with db_transaction.atomic():
                wallet = request.user.wallet
                for menu in menus:
                    key = f'menu_{menu.pk}'
                    item_id = request.POST.get(key)
                    if not item_id:
                        continue
                    if menu.pk in existing:
                        continue  # already ordered
                    item = MealItem.objects.get(pk=item_id, is_active=True)
                    if item not in menu.options.all():
                        continue
                    total_cost += item.price
                    orders_to_create.append((menu, item))

                if total_cost > 0:
                    if not wallet.can_afford(total_cost):
                        messages.error(request, _('موجودی کیف پول کافی نیست.'))
                        return redirect('cafeteria:meals')
                    wallet.withdraw(
                        total_cost,
                        description=f'سفارش غذای هفته {week_start}',
                        transaction_type=Transaction.Type.MEAL
                    )
                    for menu, item in orders_to_create:
                        MealOrder.objects.create(
                            user=request.user,
                            menu=menu,
                            meal_item=item,
                            price_at_order=item.price
                        )
                    messages.success(request, _('سفارش با موفقیت ثبت و مبلغ از کیف پول کسر شد.'))
                else:
                    messages.info(request, _('هیچ وعده جدیدی انتخاب نشده بود.'))
        except Exception as e:
            messages.error(request, str(e))
        return redirect('cafeteria:meals')

    return render(request, 'cafeteria/meals.html', {
        'menus': menus,
        'existing_orders': existing,
        'week_start': week_start,
        'balance': request.user.wallet.balance if hasattr(request.user, 'wallet') else 0,
    })
