# Generated by Django 4.2.1 on 2023-11-07 00:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('restaurant_app', '0038_product_preparation_time'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='num_of_people',
            field=models.IntegerField(default=1),
        ),
    ]
