# Generated by Django 4.2.1 on 2023-11-16 20:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('restaurant_app', '0045_alter_paymentmethod_method'),
    ]

    operations = [
        migrations.AlterField(
            model_name='paymentmethod',
            name='method',
            field=models.CharField(choices=[('CASH', 'Cash'), ('BANK', 'Bank Transfer'), ('CARD', 'Credit Card'), ('MIXED', 'Mixed')], max_length=5),
        ),
    ]