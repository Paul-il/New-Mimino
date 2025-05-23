# Generated by Django 4.2.1 on 2023-10-01 15:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('restaurant_app', '0029_alter_tipdistribution_unique_together'),
    ]

    operations = [
        migrations.AddField(
            model_name='tip',
            name='order',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='tips', to='restaurant_app.order'),
        ),
    ]
