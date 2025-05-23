# Generated by Django 4.2.1 on 2023-10-10 18:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('restaurant_app', '0030_tip_order'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='category',
            field=models.CharField(choices=[('first_dishes', 'first_dishes'), ('meat_dishes', 'meat_dishes'), ('bakery', 'bakery'), ('khinkali', 'khinkali'), ('khachapuri', 'khachapuri'), ('garnish', 'garnish'), ('grill_meat', 'grill_meat'), ('dessert', 'dessert'), ('soups', 'soups'), ('salads', 'salads'), ('delivery', 'delivery'), ('drinks', 'drinks'), ('soft_drinks', 'soft_drinks'), ('beer', 'beer'), ('wine', 'wine'), ('vodka', 'vodka'), ('cognac', 'cognac'), ('whisky', 'whisky'), ('dessert_drinks', 'dessert_drinks'), ('own_alc', 'own_alc'), ('banket', 'banket'), ('mishloha', 'mishloha')], max_length=50),
        ),
    ]
