# Generated by Django 4.2.1 on 2023-10-13 15:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('restaurant_app', '0036_alter_orderitem_order'),
    ]

    operations = [
        migrations.AddField(
            model_name='waiterorder',
            name='last_printed_comments',
            field=models.TextField(blank=True, null=True),
        ),
    ]
