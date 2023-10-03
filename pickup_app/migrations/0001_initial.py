# Generated by Django 4.1.7 on 2023-03-21 08:17

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('restaurant_app', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Cart',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('total_price', models.DecimalField(decimal_places=2, default=0, max_digits=8)),
            ],
        ),
        migrations.CreateModel(
            name='PickupOrder',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('phone', models.CharField(max_length=20)),
                ('name', models.CharField(max_length=20)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_updated', models.DateTimeField(auto_now=True)),
                ('is_completed', models.BooleanField(default=False)),
                ('status', models.CharField(choices=[('new', 'New'), ('processing', 'Processing'), ('completed', 'Completed'), ('canceled', 'Canceled')], default='new', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='OrderItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.PositiveIntegerField(default=1)),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='pickup_app.pickuporder')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='restaurant_app.product')),
            ],
        ),
        migrations.CreateModel(
            name='CartItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.PositiveIntegerField(default=1)),
                ('cart', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cart_items', to='pickup_app.cart')),
                ('pickup_order', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='cart_items', to='pickup_app.pickuporder')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='restaurant_app.product')),
            ],
        ),
        migrations.AddField(
            model_name='cart',
            name='pickup_order',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='carts', to='pickup_app.pickuporder'),
        ),
    ]