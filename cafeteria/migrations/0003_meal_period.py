from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('cafeteria', '0002_mealorder_receipt_code'),
    ]
    operations = [
        migrations.AddField(
            model_name='weeklymenu',
            name='meal_period',
            field=models.CharField(
                choices=[('breakfast', 'صبحانه'), ('lunch', 'ناهار'), ('dinner', 'شام')],
                db_index=True,
                default='lunch',
                max_length=20,
                verbose_name='وعده',
            ),
        ),
        migrations.AlterUniqueTogether(
            name='weeklymenu',
            unique_together={('week_start', 'weekday', 'meal_period')},
        ),
        migrations.AlterModelOptions(
            name='weeklymenu',
            options={
                'ordering': ['week_start', 'weekday', 'meal_period'],
                'verbose_name': 'منوی روزانه',
                'verbose_name_plural': 'منوی هفتگی',
            },
        ),
    ]
