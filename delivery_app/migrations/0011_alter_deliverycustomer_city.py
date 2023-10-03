# Generated by Django 4.0 on 2023-06-30 11:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('delivery_app', '0010_alter_deliverycustomer_city'),
    ]

    operations = [
        migrations.AlterField(
            model_name='deliverycustomer',
            name='city',
            field=models.CharField(choices=[('חיפה', 'Хайфа'), ('נשר', 'Нэшер'), ('טירת כרמל', 'Тира'), ('כפר גלים', 'Кфар Галим'), ('קריית חיים', 'Кирият Хаим'), ('קריית אתא', 'Кирият Ата'), ('קריית ביאליק', 'Кирият Биалик'), ('קריית ים', 'Кирият Ям'), ('קריית מוצקין', 'Кирият Моцкин')], max_length=50),
        ),
    ]
