# Generated by Django 4.1.7 on 2023-03-23 12:37

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('delivery_app', '0004_alter_deliverycartitem_cart'),
    ]

    operations = [
        migrations.AlterField(
            model_name='deliverycartitem',
            name='delivery_order',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='delivery_cart_items', to='delivery_app.deliveryorder'),
        ),
    ]
