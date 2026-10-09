from datetime import date
from decimal import Decimal

from django.test import TestCase
from django.urls import reverse

from accounts.models import User
from cafeteria.models import MealItem, MealOrder, WeeklyMenu
from cafeteria.views import get_current_week_start, get_today_weekday
from dormitory.models import AccessLog
from tickets.models import Ticket

PANEL_URLS = {
    'cook': ['panels:cook_dashboard', 'panels:cook_orders', 'panels:cook_items', 'panels:cook_menu'],
    'maintenance': ['panels:maintenance_dashboard', 'panels:maintenance_tickets'],
    'guard': ['panels:guard_dashboard', 'panels:guard_gate', 'panels:guard_outside', 'panels:guard_logs'],
    'manager': ['panels:manager_dashboard', 'panels:manager_users', 'panels:manager_user_create'],
}
STUDENT_URLS = ['dashboard', 'cafeteria:meals', 'wallet:wallet', 'dormitory:my_room', 'tickets:list', 'tickets:create']


def make_users():
    users = {}
    for role in ('student', 'cook', 'maintenance', 'guard', 'manager', 'admin'):
        users[role] = User.objects.create_user(
            role, password='pass12345', role=role,
            student_id='900' if role == 'student' else None,
            gender='male' if role == 'student' else None,
            first_name=role, last_name='test')
    return users


class RoleAccessMatrixTests(TestCase):
    """هر نقش فقط پنل خودش را می‌بیند؛ مدیریت/مدیر سیستم همه را."""

    def setUp(self):
        self.users = make_users()

    def get(self, role, name):
        self.client.force_login(self.users[role])
        return self.client.get(reverse(name))

    def test_each_role_can_open_own_panel(self):
        for role, names in PANEL_URLS.items():
            for name in names:
                with self.subTest(role=role, url=name):
                    self.assertEqual(self.get(role, name).status_code, 200)

    def test_other_roles_are_blocked(self):
        for panel, names in PANEL_URLS.items():
            for role in ('student', 'cook', 'maintenance', 'guard'):
                if role == panel:
                    continue
                for name in names:
                    with self.subTest(role=role, url=name):
                        r = self.get(role, name)
                        self.assertEqual(r.status_code, 302)
                        self.assertNotIn('login', r.url)

    def test_manager_and_admin_open_every_panel(self):
        for role in ('manager', 'admin'):
            for names in PANEL_URLS.values():
                for name in names:
                    with self.subTest(role=role, url=name):
                        self.assertEqual(self.get(role, name).status_code, 200)

    def test_anonymous_redirected_to_login(self):
        for names in PANEL_URLS.values():
            for name in names:
                r = self.client.get(reverse(name))
                self.assertEqual(r.status_code, 302)
                self.assertIn('login', r.url)

    def test_dashboard_redirects_to_role_panel(self):
        expected = {
            'cook': 'panels:cook_dashboard', 'maintenance': 'panels:maintenance_dashboard',
            'guard': 'panels:guard_dashboard', 'manager': 'panels:manager_dashboard',
            'admin': 'panels:manager_dashboard',
        }
        for role, target in expected.items():
            with self.subTest(role=role):
                r = self.get(role, 'dashboard')
                self.assertRedirects(r, reverse(target))
        self.assertEqual(self.get('student', 'dashboard').status_code, 200)

    def test_student_pages_blocked_for_staff(self):
        for role in ('cook', 'maintenance', 'guard', 'manager'):
            for name in ('cafeteria:meals', 'wallet:wallet', 'dormitory:my_room'):
                with self.subTest(role=role, url=name):
                    self.assertEqual(self.get(role, name).status_code, 302)

    def test_student_pages_work_for_student(self):
        for name in STUDENT_URLS:
            with self.subTest(url=name):
                self.assertEqual(self.get('student', name).status_code, 200)

    def test_profile_and_settings_for_every_role(self):
        for role in self.users:
            for name in ('accounts:profile', 'accounts:settings'):
                with self.subTest(role=role, url=name):
                    self.assertEqual(self.get(role, name).status_code, 200)

    def test_login_redirects_each_role_to_its_panel(self):
        for role, target in [('cook', 'panels:cook_dashboard'), ('guard', 'panels:guard_dashboard'),
                             ('maintenance', 'panels:maintenance_dashboard'), ('manager', 'panels:manager_dashboard')]:
            self.client.logout()
            r = self.client.post(reverse('accounts:login'), {'username': role, 'password': 'pass12345'}, follow=True)
            self.assertEqual(r.redirect_chain[-1][0], reverse(target), role)


class ManagerUserManagementTests(TestCase):
    def setUp(self):
        self.users = make_users()
        self.client.force_login(self.users['manager'])

    def payload(self, **kw):
        data = {'username': 'newbie', 'first_name': 'ن', 'last_name': 'ج', 'email': 'a@b.com',
                'phone': '0912', 'role': 'cook', 'gender': '', 'student_id': '',
                'password1': 'Str0ng-pass-91', 'password2': 'Str0ng-pass-91'}
        data.update(kw)
        return data

    def test_create_user_for_each_staff_role(self):
        for role in ('cook', 'maintenance', 'guard', 'manager'):
            r = self.client.post(reverse('panels:manager_user_create'), self.payload(username=f'n_{role}', role=role))
            self.assertRedirects(r, reverse('panels:manager_users'))
            u = User.objects.get(username=f'n_{role}')
            self.assertEqual(u.role, role)
            self.assertTrue(u.check_password('Str0ng-pass-91'))

    def test_created_cook_logs_in_and_lands_on_cook_panel(self):
        self.client.post(reverse('panels:manager_user_create'), self.payload())
        self.client.logout()
        r = self.client.post(reverse('accounts:login'), {'username': 'newbie', 'password': 'Str0ng-pass-91'}, follow=True)
        self.assertEqual(r.redirect_chain[-1][0], reverse('panels:cook_dashboard'))

    def test_student_requires_student_id_and_section(self):
        r = self.client.post(reverse('panels:manager_user_create'), self.payload(role='student'))
        self.assertEqual(r.status_code, 200)
        self.assertFalse(User.objects.filter(username='newbie').exists())
        r = self.client.post(reverse('panels:manager_user_create'),
                             self.payload(role='student', student_id='777', gender='female'))
        self.assertEqual(r.status_code, 302)
        self.assertTrue(User.objects.get(username='newbie').is_student)

    def test_manager_cannot_create_admin(self):
        self.client.post(reverse('panels:manager_user_create'), self.payload(role='admin'))
        self.assertFalse(User.objects.filter(username='newbie').exists())

    def test_admin_can_create_admin(self):
        self.client.force_login(self.users['admin'])
        self.client.post(reverse('panels:manager_user_create'), self.payload(role='admin'))
        self.assertEqual(User.objects.get(username='newbie').role, 'admin')

    def test_password_mismatch_and_weak_password_rejected(self):
        self.client.post(reverse('panels:manager_user_create'), self.payload(password2='other'))
        self.client.post(reverse('panels:manager_user_create'), self.payload(password1='123', password2='123'))
        self.assertFalse(User.objects.filter(username='newbie').exists())

    def test_duplicate_blank_student_ids_dont_clash(self):
        self.client.post(reverse('panels:manager_user_create'), self.payload(username='c1'))
        r = self.client.post(reverse('panels:manager_user_create'), self.payload(username='c2'))
        self.assertEqual(r.status_code, 302)

    def test_change_role(self):
        cook = self.users['cook']
        r = self.client.post(reverse('panels:manager_user_edit', args=[cook.pk]), {
            'action': 'save', 'first_name': 'a', 'last_name': 'b', 'email': '', 'phone': '',
            'role': 'guard', 'gender': '', 'student_id': '', 'is_active': 'on'})
        self.assertEqual(r.status_code, 302)
        cook.refresh_from_db()
        self.assertEqual(cook.role, 'guard')

    def test_manager_cannot_edit_admin(self):
        r = self.client.get(reverse('panels:manager_user_edit', args=[self.users['admin'].pk]))
        self.assertEqual(r.status_code, 302)
        self.client.post(reverse('panels:manager_user_toggle', args=[self.users['admin'].pk]))
        self.users['admin'].refresh_from_db()
        self.assertTrue(self.users['admin'].is_active)

    def test_cannot_deactivate_self(self):
        self.client.post(reverse('panels:manager_user_toggle', args=[self.users['manager'].pk]))
        self.users['manager'].refresh_from_db()
        self.assertTrue(self.users['manager'].is_active)

    def test_deactivate_user_blocks_login(self):
        cook = self.users['cook']
        self.client.post(reverse('panels:manager_user_toggle', args=[cook.pk]))
        self.client.logout()
        self.assertFalse(self.client.login(username='cook', password='pass12345'))

    def test_reset_password_and_charge_wallet(self):
        stu = self.users['student']
        url = reverse('panels:manager_user_edit', args=[stu.pk])
        self.client.post(url, {'action': 'password', 'password1': 'Another-p4ss!x', 'password2': 'Another-p4ss!x'})
        stu.refresh_from_db()
        self.assertTrue(stu.check_password('Another-p4ss!x'))
        self.client.post(url, {'action': 'charge', 'amount': '50000', 'description': 'test'})
        stu.wallet.refresh_from_db()
        self.assertEqual(stu.wallet.balance, Decimal('50000'))

    def test_users_list_filter(self):
        r = self.client.get(reverse('panels:manager_users') + '?role=cook')
        self.assertContains(r, 'cook')
        self.assertEqual(r.status_code, 200)

    def test_non_managers_cannot_create_users(self):
        for role in ('student', 'cook', 'guard', 'maintenance'):
            self.client.force_login(self.users[role])
            self.client.post(reverse('panels:manager_user_create'), self.payload(username=f'x_{role}'))
            self.assertFalse(User.objects.filter(username=f'x_{role}').exists())


class CookPanelTests(TestCase):
    def setUp(self):
        self.users = make_users()
        self.client.force_login(self.users['cook'])
        self.item = MealItem.objects.create(name_fa='کباب', price=Decimal('70000'))
        self.item2 = MealItem.objects.create(name_fa='عدس‌پلو', price=Decimal('30000'))

    def test_set_weekly_menu_and_orders_flow(self):
        ws = get_current_week_start()
        r = self.client.post(reverse('panels:cook_menu'), {'day_0': [self.item.pk, self.item2.pk], 'day_1': [self.item.pk]})
        self.assertEqual(r.status_code, 302)
        self.assertEqual(WeeklyMenu.objects.get(week_start=ws, weekday=0).options.count(), 2)
        self.assertEqual(WeeklyMenu.objects.filter(week_start=ws).count(), 2)

    def test_menu_save_keeps_already_ordered_items(self):
        ws = get_current_week_start()
        menu = WeeklyMenu.objects.create(week_start=ws, weekday=0)
        menu.options.set([self.item, self.item2])
        MealOrder.objects.create(user=self.users['student'], menu=menu, meal_item=self.item, price_at_order=1)
        self.client.post(reverse('panels:cook_menu'), {'day_0': [self.item2.pk]})
        self.assertEqual(set(menu.options.all()), {self.item, self.item2})

    def test_serve_toggle_and_totals(self):
        today = date.today()
        menu = WeeklyMenu.objects.create(week_start=get_current_week_start(today), weekday=get_today_weekday(today))
        menu.options.set([self.item])
        o = MealOrder.objects.create(user=self.users['student'], menu=menu, meal_item=self.item, price_at_order=70000)
        self.assertContains(self.client.get(reverse('panels:cook_dashboard')), 'کباب')
        self.assertContains(self.client.get(reverse('panels:cook_orders')), 'student')
        self.client.post(reverse('panels:cook_serve', args=[o.pk]))
        o.refresh_from_db()
        self.assertTrue(o.is_served)
        self.assertEqual(o.served_by, self.users['cook'])
        self.client.post(reverse('panels:cook_serve', args=[o.pk]))
        o.refresh_from_db()
        self.assertFalse(o.is_served)

    def test_item_create_edit_toggle(self):
        self.client.post(reverse('panels:cook_items'), {'name_fa': 'سالاد', 'price': '15000', 'is_active': 'on'})
        item = MealItem.objects.get(name_fa='سالاد')
        self.client.post(reverse('panels:cook_items') + f'?edit={item.pk}', {'name_fa': 'سالاد', 'price': '20000', 'is_active': 'on'})
        item.refresh_from_db()
        self.assertEqual(item.price, 20000)
        self.client.post(reverse('panels:cook_item_toggle', args=[item.pk]))
        item.refresh_from_db()
        self.assertFalse(item.is_active)

    def test_bad_date_param_is_safe(self):
        self.assertEqual(self.client.get(reverse('panels:cook_orders') + '?date=garbage').status_code, 200)


class MaintenanceAndTicketTests(TestCase):
    def setUp(self):
        self.users = make_users()
        self.ticket = Ticket.objects.create(user=self.users['student'], subject='پریز خراب', description='x', category='electric')

    def test_maintenance_lists_and_updates_ticket(self):
        self.client.force_login(self.users['maintenance'])
        self.assertContains(self.client.get(reverse('panels:maintenance_tickets')), 'پریز خراب')
        url = reverse('tickets:detail', args=[self.ticket.pk])
        self.assertEqual(self.client.get(url).status_code, 200)
        self.client.post(url, {'action': 'assign_me'})
        self.ticket.refresh_from_db()
        self.assertEqual(self.ticket.assigned_to, self.users['maintenance'])
        self.assertEqual(self.ticket.status, 'in_progress')
        self.client.post(url, {'action': 'status', 'status': 'resolved'})
        self.ticket.refresh_from_db()
        self.assertEqual(self.ticket.status, 'resolved')
        self.client.post(url, {'message': 'درست شد'})
        self.assertTrue(self.ticket.replies.get().is_staff_reply)

    def test_student_cannot_change_status_or_see_others(self):
        self.client.force_login(self.users['student'])
        url = reverse('tickets:detail', args=[self.ticket.pk])
        self.client.post(url, {'action': 'status', 'status': 'closed'})
        self.ticket.refresh_from_db()
        self.assertEqual(self.ticket.status, 'open')
        other = User.objects.create_user('o', password='x', student_id='5')
        self.client.force_login(other)
        self.assertEqual(self.client.get(url).status_code, 302)

    def test_cook_and_guard_cannot_open_ticket(self):
        for role in ('cook', 'guard'):
            self.client.force_login(self.users[role])
            self.assertEqual(self.client.get(reverse('tickets:detail', args=[self.ticket.pk])).status_code, 302)

    def test_dashboard_renders_with_data(self):
        self.client.force_login(self.users['maintenance'])
        Ticket.objects.create(user=self.users['student'], subject='فوری', description='x', priority='urgent')
        self.assertContains(self.client.get(reverse('panels:maintenance_dashboard')), 'فوری')


class GuardPanelTests(TestCase):
    def setUp(self):
        self.users = make_users()
        self.client.force_login(self.users['guard'])
        self.student = self.users['student']

    def test_record_in_out_and_outside_list(self):
        r = self.client.post(reverse('panels:guard_record'), {'user_id': self.student.pk, 'direction': 'out', 'note': 'شهر'})
        self.assertEqual(r.status_code, 302)
        self.assertContains(self.client.get(reverse('panels:guard_outside')), 'student')
        self.client.post(reverse('panels:guard_record'), {'user_id': self.student.pk, 'direction': 'in'})
        self.assertNotContains(self.client.get(reverse('panels:guard_outside')), '900')
        self.assertEqual(AccessLog.objects.filter(user=self.student, recorded_by=self.users['guard']).count(), 2)

    def test_search_and_logs(self):
        self.assertContains(self.client.get(reverse('panels:guard_gate') + '?q=900'), 'student')
        self.client.post(reverse('panels:guard_record'), {'user_id': self.student.pk, 'direction': 'out'})
        self.assertContains(self.client.get(reverse('panels:guard_logs')), 'خروج')
        self.assertEqual(self.client.get(reverse('panels:guard_logs') + '?date=bad').status_code, 200)

    def test_invalid_direction_rejected(self):
        self.client.post(reverse('panels:guard_record'), {'user_id': self.student.pk, 'direction': 'sideways'})
        self.assertEqual(AccessLog.objects.count(), 0)

    def test_guard_cannot_log_non_students(self):
        self.client.post(reverse('panels:guard_record'), {'user_id': self.users['cook'].pk, 'direction': 'in'})
        self.assertEqual(AccessLog.objects.count(), 0)

    def test_guard_limited_to_own_section(self):
        female = User.objects.create_user('fem', password='x', role='student', student_id='42', gender='female')
        guard = self.users['guard']
        guard.gender = 'male'
        guard.save()
        self.client.post(reverse('panels:guard_record'), {'user_id': female.pk, 'direction': 'out'})
        self.assertEqual(AccessLog.objects.count(), 0)
        self.assertContains(self.client.get(reverse('panels:guard_gate') + '?q=fem'), 'دانشجویی یافت نشد')

    def test_students_cannot_record(self):
        self.client.force_login(self.student)
        self.client.post(reverse('panels:guard_record'), {'user_id': self.student.pk, 'direction': 'out'})
        self.assertEqual(AccessLog.objects.count(), 0)
