# Generated by Django 4.0 on 2023-09-21 10:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('restaurant_app', '0026_alter_product_printer'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='printer',
            field=models.CharField(choices=[('print80', 'Кухня 1'), ('Printer80', 'Кухня 2'), ('Printer80-2', 'Бар')], default='kitchen_1', max_length=50, verbose_name='Принтер'),
        ),
    ]