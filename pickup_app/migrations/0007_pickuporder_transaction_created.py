# Generated by Django 5.0.1 on 2024-06-10 10:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pickup_app', '0006_pickuporder_cart_snapshot'),
    ]

    operations = [
        migrations.AddField(
            model_name='pickuporder',
            name='transaction_created',
            field=models.BooleanField(default=False),
        ),
    ]