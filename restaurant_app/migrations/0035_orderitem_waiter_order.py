# Generated by Django 4.2.1 on 2023-10-13 11:32

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('restaurant_app', '0034_remove_order_user_waiterorder'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderitem',
            name='waiter_order',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='waiter_order_items', to='restaurant_app.waiterorder'),
        ),
    ]
