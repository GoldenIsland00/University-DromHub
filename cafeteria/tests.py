from datetime import date
from decimal import Decimal
from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse

from accounts.models import User
from cafeteria.models import MealItem, MealOrder, WeeklyMenu

FAKE_TODAY = date(2026, 10, 7)       # چهارشنبه
WEEK_START = date(2026, 10, 3)       # شنبه همان هفته


@patch('django.utils.timezone.localdate', return_value=FAKE_TODAY)
class StudentMealOrderTests(TestCase):
    def setUp(self):
        self.student = User.objects.create_user(
            'stu', password='x', role='student', student_id='1', gender='male')
        self.student.wallet.deposit(200000)
        self.rice = MealItem.objects.create(name_fa='چلو مرغ', price=Decimal('50000'))
        self.stew = MealItem.objects.create(name_fa='قرمه سبزی', price=Decimal('60000'))
        self.menus = {}
        for weekday in (2, 4, 5):    # دوشنبه (گذشته)، چهارشنبه (امروز)، پنج‌شنبه (آینده)
            m = WeeklyMenu.objects.create(week_start=WEEK_START, weekday=weekday)
            m.options.set([self.rice, self.stew])
            self.menus[weekday] = m
        self.client.force_login(self.student)
        self.url = reverse('cafeteria:meals')

    def test_page_renders(self, _):
        r = self.client.get(self.url)
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, 'چلو مرغ')

    def test_next_week_page_renders(self, _):
        self.assertEqual(self.client.get(self.url + '?week=next').status_code, 200)

    def test_order_deducts_wallet_and_creates_orders(self, _):
        r = self.client.post(self.url, {
            f'menu_{self.menus[4].pk}': self.rice.pk,
            f'menu_{self.menus[5].pk}': self.stew.pk,
        })
        self.assertRedirects(r, self.url)
        self.assertEqual(MealOrder.objects.filter(user=self.student).count(), 2)
        self.student.wallet.refresh_from_db()
        self.assertEqual(self.student.wallet.balance, Decimal('90000'))
        self.assertEqual(self.student.wallet.transactions.filter(transaction_type='meal').count(), 2)

    def test_insufficient_balance_creates_nothing(self, _):
        self.student.wallet.withdraw(180000)   # باقی‌مانده ۲۰٬۰۰۰
        self.client.post(self.url, {f'menu_{self.menus[4].pk}': self.rice.pk})
        self.assertEqual(MealOrder.objects.count(), 0)
        self.student.wallet.refresh_from_db()
        self.assertEqual(self.student.wallet.balance, Decimal('20000'))

    def test_cannot_order_past_day(self, _):
        self.client.post(self.url, {f'menu_{self.menus[2].pk}': self.rice.pk})
        self.assertEqual(MealOrder.objects.count(), 0)

    def test_cannot_order_item_not_in_menu(self, _):
        other = MealItem.objects.create(name_fa='سایر', price=Decimal('1000'))
        self.client.post(self.url, {f'menu_{self.menus[4].pk}': other.pk})
        self.assertEqual(MealOrder.objects.count(), 0)

    def test_no_double_charge_for_same_day(self, _):
        data = {f'menu_{self.menus[4].pk}': self.rice.pk}
        self.client.post(self.url, data)
        self.client.post(self.url, data)
        self.assertEqual(MealOrder.objects.count(), 1)
        self.student.wallet.refresh_from_db()
        self.assertEqual(self.student.wallet.balance, Decimal('150000'))

    def test_cancel_future_order_refunds(self, _):
        self.client.post(self.url, {f'menu_{self.menus[5].pk}': self.stew.pk})
        order = MealOrder.objects.get()
        self.client.post(reverse('cafeteria:cancel', args=[order.pk]))
        self.assertEqual(MealOrder.objects.count(), 0)
        self.student.wallet.refresh_from_db()
        self.assertEqual(self.student.wallet.balance, Decimal('200000'))
        self.assertTrue(self.student.wallet.transactions.filter(transaction_type='refund').exists())

    def test_cannot_cancel_todays_order(self, _):
        self.client.post(self.url, {f'menu_{self.menus[4].pk}': self.rice.pk})
        order = MealOrder.objects.get()
        self.client.post(reverse('cafeteria:cancel', args=[order.pk]))
        self.assertEqual(MealOrder.objects.count(), 1)

    def test_cannot_cancel_someone_elses_order(self, _):
        other = User.objects.create_user('o', password='x', role='student', student_id='2')
        order = MealOrder.objects.create(user=other, menu=self.menus[5], meal_item=self.rice, price_at_order=50000)
        r = self.client.post(reverse('cafeteria:cancel', args=[order.pk]))
        self.assertEqual(r.status_code, 404)
