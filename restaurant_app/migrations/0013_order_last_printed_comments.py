# Generated by Django 4.0 on 2023-05-04 19:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('restaurant_app', '0012_order_comments'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='last_printed_comments',
            field=models.TextField(blank=True, null=True),
        ),
    ]
