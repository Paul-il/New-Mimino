# Generated by Django 5.0.1 on 2024-06-18 14:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('delivery_app', '0022_deliveryorder_transaction_created'),
    ]

    operations = [
        migrations.AddField(
            model_name='deliverycart',
            name='is_completed',
            field=models.BooleanField(default=False),
        ),
    ]
