# Generated by Django 5.0.1 on 2024-06-10 10:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('restaurant_app', '0073_product_is_available_for_delivery'),
    ]

    operations = [
        migrations.CreateModel(
            name='DeliveryOrder',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_completed', models.BooleanField(default=False)),
                ('transaction_created', models.BooleanField(default=False)),
                ('total_amount', models.DecimalField(decimal_places=2, max_digits=10, null=True)),
                ('delivery_date', models.DateField()),
                ('payment_method', models.CharField(max_length=20)),
            ],
        ),
    ]