from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('dormitory', '0001_initial'),
    ]
    operations = [
        migrations.CreateModel(
            name='LeaveRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_at', models.DateTimeField(verbose_name='شروع خروج')),
                ('end_at', models.DateTimeField(verbose_name='زمان بازگشت پیش‌بینی‌شده')),
                ('reason', models.TextField(max_length=500, verbose_name='دلیل')),
                ('destination', models.CharField(blank=True, max_length=200, verbose_name='مقصد')),
                ('status', models.CharField(choices=[('pending', 'در انتظار'), ('approved', 'تأیید شده'), ('rejected', 'رد شده'), ('cancelled', 'لغو شده')], default='pending', max_length=20)),
                ('review_note', models.CharField(blank=True, max_length=255, verbose_name='یادداشت بررسی')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('reviewed_at', models.DateTimeField(blank=True, null=True)),
                ('reviewed_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='reviewed_leaves', to=settings.AUTH_USER_MODEL, verbose_name='بررسی‌کننده')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='leave_requests', to=settings.AUTH_USER_MODEL, verbose_name='دانشجو')),
            ],
            options={'verbose_name': 'درخواست مرخصی', 'verbose_name_plural': 'درخواست‌های مرخصی', 'ordering': ['-created_at']},
        ),
    ]
