from decimal import Decimal
from django.conf import settings
from django.db import migrations, models
import django.core.validators
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('wallet', '0001_initial'),
    ]
    operations = [
        migrations.CreateModel(
            name='PaymentRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=0, max_digits=12, validators=[django.core.validators.MinValueValidator(Decimal('1000'))], verbose_name='مبلغ')),
                ('authority', models.CharField(db_index=True, max_length=64, unique=True, verbose_name='شناسه پیگیری')),
                ('status', models.CharField(choices=[('pending', 'در انتظار پرداخت'), ('success', 'موفق'), ('failed', 'ناموفق'), ('cancelled', 'لغو شده')], default='pending', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('paid_at', models.DateTimeField(blank=True, null=True)),
                ('gateway', models.CharField(default='mock', max_length=50, verbose_name='درگاه')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='payment_requests', to=settings.AUTH_USER_MODEL, verbose_name='کاربر')),
            ],
            options={'verbose_name': 'درخواست پرداخت', 'verbose_name_plural': 'درخواست‌های پرداخت', 'ordering': ['-created_at']},
        ),
    ]
