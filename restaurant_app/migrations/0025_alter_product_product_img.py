# Generated by Django 4.2.1 on 2023-09-21 08:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('restaurant_app', '0024_product_printer'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='product_img',
            field=models.ImageField(blank=True, null=True, upload_to='product_images/'),
        ),
    ]
