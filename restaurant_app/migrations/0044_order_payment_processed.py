# Generated by Django 4.2.1 on 2023-11-16 18:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('restaurant_app', '0043_alter_order_payment_method'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='payment_processed',
            field=models.BooleanField(default=False),
        ),
    ]
