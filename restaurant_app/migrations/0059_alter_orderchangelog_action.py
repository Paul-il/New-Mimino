# Generated by Django 5.0.1 on 2024-03-03 17:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('restaurant_app', '0058_orderchangelog_order_item'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderchangelog',
            name='action',
            field=models.CharField(choices=[('add', 'Добавили'), ('decrease', 'Уменьщили'), ('delete', 'Удалили')], max_length=10),
        ),
    ]
