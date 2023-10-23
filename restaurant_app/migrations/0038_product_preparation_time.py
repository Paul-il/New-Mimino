# Generated by Django 4.2.1 on 2023-10-20 15:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('restaurant_app', '0037_waiterorder_last_printed_comments'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='preparation_time',
            field=models.PositiveIntegerField(blank=True, default=0, verbose_name='Время приготовления (в минутах)'),
        ),
    ]
