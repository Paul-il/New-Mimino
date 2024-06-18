# Generated by Django 4.2.1 on 2023-11-23 20:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('restaurant_app', '0053_order_is_bill_printed'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderitem',
            name='discount_percentage',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=5, verbose_name='Процент скидки'),
        ),
    ]
