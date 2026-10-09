from django.db import migrations, models
import secrets


def gen_code():
    alphabet = 'ABCDEFGHJKMNPQRSTUVWXYZ23456789'
    return ''.join(secrets.choice(alphabet) for _ in range(6))


def fill_receipt_codes(apps, schema_editor):
    MealOrder = apps.get_model('cafeteria', 'MealOrder')
    used = set(
        MealOrder.objects.exclude(receipt_code__isnull=True)
        .exclude(receipt_code='')
        .values_list('receipt_code', flat=True)
    )
    for order in MealOrder.objects.all():
        if order.receipt_code:
            continue
        for _ in range(100):
            code = gen_code()
            if code not in used:
                used.add(code)
                order.receipt_code = code
                order.save(update_fields=['receipt_code'])
                break


class Migration(migrations.Migration):

    dependencies = [
        ('cafeteria', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='mealorder',
            name='receipt_code',
            field=models.CharField(
                blank=True,
                db_index=True,
                help_text='کد یکتای هر وعده برای تحویل در سلف',
                max_length=12,
                null=True,
                unique=True,
                verbose_name='کد فیش',
            ),
        ),
        migrations.RunPython(fill_receipt_codes, migrations.RunPython.noop),
    ]
