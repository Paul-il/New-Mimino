# Generated by Django 4.2.1 on 2023-09-21 09:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('restaurant_app', '0025_alter_product_product_img'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='printer',
            field=models.CharField(choices=[('kitchen_1', 'Кухня 1'), ('kitchen_2', 'Кухня 2'), ('kitchen_3', 'Бар')], default='kitchen_1', max_length=50, verbose_name='Принтер'),
        ),
    ]
