# Generated by Django 4.2.1 on 2023-10-03 19:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pickup_app', '0003_cartitem_printed_quantity'),
    ]

    operations = [
        migrations.AddField(
            model_name='pickuporder',
            name='total_amount',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
    ]
