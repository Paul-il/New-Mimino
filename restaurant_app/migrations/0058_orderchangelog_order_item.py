# Generated by Django 5.0.1 on 2024-03-03 13:40

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('restaurant_app', '0057_alter_orderchangelog_action'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderchangelog',
            name='order_item',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='restaurant_app.orderitem'),
        ),
    ]