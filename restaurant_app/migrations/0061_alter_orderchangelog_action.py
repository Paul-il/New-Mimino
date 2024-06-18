# Generated by Django 5.0.1 on 2024-03-03 17:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('restaurant_app', '0060_alter_orderchangelog_action'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderchangelog',
            name='action',
            field=models.CharField(choices=[('add', 'Добавили'), ('decrease', 'Убавили'), ('delete', 'Удалили'), ('increase', 'Прибавили')], max_length=10),
        ),
    ]
