# Generated by Django 4.2.1 on 2023-07-07 15:06

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='StatisticsOrder',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_completed', models.BooleanField(default=False)),
                ('comments', models.TextField(blank=True, null=True)),
                ('last_printed_comments', models.TextField(blank=True, null=True)),
                ('table_number', models.IntegerField()),
                ('total_price', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('status', models.CharField(max_length=20)),
                ('payment_method', models.CharField(blank=True, max_length=10, null=True)),
            ],
            options={
                'db_table': 'restaurant_app_order',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='StatisticsOrderItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.PositiveIntegerField(default=1)),
                ('phone_number', models.CharField(max_length=10)),
                ('printed', models.BooleanField(default=False)),
                ('printed_quantity', models.IntegerField(default=0)),
            ],
            options={
                'db_table': 'restaurant_app_orderitem',
                'managed': False,
            },
        ),
    ]
