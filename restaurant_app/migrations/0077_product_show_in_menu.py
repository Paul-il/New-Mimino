# Generated by Django 5.0.1 on 2024-07-14 17:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('restaurant_app', '0076_alter_order_table_number'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='show_in_menu',
            field=models.BooleanField(default=True, verbose_name='Показывать в меню'),
        ),
    ]