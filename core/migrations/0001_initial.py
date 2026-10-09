from decimal import Decimal
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]
    operations = [
        migrations.CreateModel(
            name='SystemSettings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('site_name', models.CharField(default='سامانه خوابگاه و سلف', max_length=120, verbose_name='نام سامانه')),
                ('order_cutoff_hour', models.PositiveSmallIntegerField(default=10, help_text='بعد از این ساعت (۰–۲۳) نمی‌توان برای امروز سفارش داد', verbose_name='ساعت قطع سفارش همان روز')),
                ('low_balance_threshold', models.DecimalField(decimal_places=0, default=Decimal('50000'), max_digits=12, verbose_name='آستانه هشدار موجودی کم')),
                ('allow_student_charge', models.BooleanField(default=True, verbose_name='اجازه شارژ آنلاین توسط دانشجو')),
                ('mock_payment_enabled', models.BooleanField(default=True, verbose_name='درگاه ساختگی (دمو) فعال باشد')),
                ('breakfast_enabled', models.BooleanField(default=True, verbose_name='فعال بودن صبحانه')),
                ('lunch_enabled', models.BooleanField(default=True, verbose_name='فعال بودن ناهار')),
                ('dinner_enabled', models.BooleanField(default=True, verbose_name='فعال بودن شام')),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={'verbose_name': 'تنظیمات سیستم', 'verbose_name_plural': 'تنظیمات سیستم'},
        ),
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('kind', models.CharField(choices=[('info', 'اطلاع'), ('success', 'موفق'), ('warning', 'هشدار'), ('ticket', 'تیکت'), ('meal', 'غذا'), ('wallet', 'کیف پول'), ('leave', 'مرخصی')], default='info', max_length=20)),
                ('title', models.CharField(max_length=200, verbose_name='عنوان')),
                ('body', models.TextField(blank=True, verbose_name='متن')),
                ('link', models.CharField(blank=True, max_length=300, verbose_name='لینک')),
                ('is_read', models.BooleanField(default=False, verbose_name='خوانده شده')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notifications', to=settings.AUTH_USER_MODEL, verbose_name='کاربر')),
            ],
            options={'verbose_name': 'اعلان', 'verbose_name_plural': 'اعلان‌ها', 'ordering': ['-created_at']},
        ),
    ]
