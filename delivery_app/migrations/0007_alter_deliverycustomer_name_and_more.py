# Generated by Django 4.0 on 2023-04-20 09:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('delivery_app', '0006_alter_deliverycustomer_street'),
    ]

    operations = [
        migrations.AlterField(
            model_name='deliverycustomer',
            name='name',
            field=models.CharField(max_length=30),
        ),
        migrations.AlterField(
            model_name='deliverycustomer',
            name='street',
            field=models.CharField(max_length=50),
        ),
    ]
