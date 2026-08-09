from datetime import date, timedelta
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from dormitory.models import Building, Room, Bed
from cafeteria.models import MealItem, WeeklyMenu
from wallet.models import Wallet

User = get_user_model()


class Command(BaseCommand):
    help = 'Seed demo data for dormitory system'

    def handle(self, *args, **options):
        self.stdout.write('Seeding demo data...')

        # Admin
        admin, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@uni.ac.ir',
                'first_name': 'مدیر',
                'last_name': 'سیستم',
                'role': User.Role.ADMIN,
                'is_staff': True,
                'is_superuser': True,
            }
        )
        if created:
            admin.set_password('admin1234')
            admin.save()
            self.stdout.write(self.style.SUCCESS('Admin created: admin / admin1234'))

        # Buildings
        male_b, _ = Building.objects.get_or_create(name='ساختمان A', section='male', defaults={'floors': 4})
        female_b, _ = Building.objects.get_or_create(name='ساختمان B', section='female', defaults={'floors': 4})

        # Rooms + Beds
        for b, prefix in [(male_b, 300), (female_b, 200)]:
            for floor in range(1, 3):
                for n in range(1, 5):
                    num = f"{prefix + floor * 10 + n}"
                    room, created = Room.objects.get_or_create(
                        building=b, number=num,
                        defaults={'floor': floor, 'capacity': 4}
                    )
                    if created:
                        for bed_n in range(1, 5):
                            Bed.objects.get_or_create(room=room, number=bed_n)

        # Demo students
        students = [
            ('ali', 'علی', 'محمدی', 'male', '4012345678', '09121234567'),
            ('reza', 'رضا', 'کریمی', 'male', '4012345679', '09121234568'),
            ('zahra', 'زهرا', 'احمدی', 'female', '4012345701', '09121234569'),
        ]
        for uname, first, last, gender, sid, phone in students:
            u, created = User.objects.get_or_create(
                username=uname,
                defaults={
                    'first_name': first,
                    'last_name': last,
                    'email': f'{uname}@uni.ac.ir',
                    'student_id': sid,
                    'phone': phone,
                    'gender': gender,
                    'role': User.Role.STUDENT,
                }
            )
            if created:
                u.set_password('student1234')
                u.save()
                Wallet.objects.get_or_create(user=u)
                u.wallet.deposit(300000, description='شارژ اولیه')

        # Assign beds
        ali = User.objects.get(username='ali')
        reza = User.objects.get(username='reza')
        zahra = User.objects.get(username='zahra')
        room_304 = Room.objects.filter(number='311').first() or Room.objects.filter(building=male_b).first()
        if room_304:
            beds = list(room_304.beds.order_by('number'))
            if len(beds) >= 2:
                beds[0].occupant = ali
                beds[0].save()
                beds[1].occupant = reza
                beds[1].save()
        room_f = Room.objects.filter(building=female_b).first()
        if room_f:
            bed = room_f.beds.first()
            if bed:
                bed.occupant = zahra
                bed.save()

        # Meal items
        meals = [
            ('چلو مرغ', 'Chicken Rice', 45000),
            ('چلو گوشت', 'Meat Rice', 55000),
            ('عدس پلو', 'Lentil Rice', 35000),
            ('قرمه سبزی', 'Ghormeh Sabzi', 50000),
            ('جوجه کباب', 'Joojeh Kebab', 60000),
            ('ماش پلو', 'Mung Bean Rice', 32000),
            ('خوراک مرغ', 'Chicken Stew', 48000),
            ('چلو کباب', 'Kebab Rice', 65000),
        ]
        items = []
        for fa, en, price in meals:
            item, _ = MealItem.objects.get_or_create(
                name_fa=fa,
                defaults={'name_en': en, 'price': Decimal(price)}
            )
            items.append(item)

        # Weekly menu
        today = date.today()
        days_since_sat = (today.weekday() + 2) % 7
        week_start = today - timedelta(days=days_since_sat)
        for day in range(7):
            menu, created = WeeklyMenu.objects.get_or_create(
                week_start=week_start,
                weekday=day
            )
            if created or menu.options.count() == 0:
                menu.options.set(items[day % len(items): day % len(items) + 3])

        self.stdout.write(self.style.SUCCESS('Demo data seeded successfully!'))
        self.stdout.write('Students: ali / student1234 , reza / student1234 , zahra / student1234')
        self.stdout.write('Admin: admin / admin1234')
