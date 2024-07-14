from django.db import models
from django import forms
from django.conf import settings
from django.urls import reverse

class Product(models.Model):
    CATEGORY_CHOICES = [
        ('first_dishes', 'first_dishes'),
        ('meat_dishes', 'meat_dishes'),
        ('bakery', 'bakery'),
        ('khinkali', 'khinkali'),
        ('khachapuri', 'khachapuri'),
        ('garnish', 'garnish'),
        ('grill_meat', 'grill_meat'),
        ('dessert', 'dessert'),
        ('soups', 'soups'),
        ('salads', 'salads'),
        ('sales', 'sales'),
        ('delivery', 'delivery'),
        ('drinks', 'drinks'),
        ('soft_drinks', 'soft_drinks'),
        ('beer', 'beer'),
        ('wine', 'wine'),
        ('vodka', 'vodka'),
        ('cognac', 'cognac'),
        ('whisky', 'whisky'),
        ('dessert_drinks', 'dessert_drinks'),
        ('own_alc', 'own_alc'),
        ('banket', 'banket'),
        ('mishloha', 'mishloha'),
    ]

    PRINTER_CHOICES = [
        ('print80', 'Бар'),
        ('Printer80', 'Мал Кухня'),
        ('Printer80-2', 'Бол Кухня'),
    ]

    id = models.AutoField(primary_key=True)
    product_name_rus = models.CharField(max_length=100, verbose_name='Название блюда (рус.)')
    product_name_heb = models.CharField(max_length=100, verbose_name='שם מנה (עברית)')
    product_price = models.DecimalField(max_digits=6, decimal_places=2, verbose_name='Цена продукта')
    product_img = models.ImageField(upload_to='product_images/', blank=True, null=True)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    printer = models.CharField(max_length=50, choices=PRINTER_CHOICES, default='print80', verbose_name='Принтер')
    created_at = models.DateTimeField(auto_now_add=True)
    quantity = models.PositiveIntegerField(default=1)
    delivery_price = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    is_available = models.BooleanField(default=True)
    preparation_time = models.PositiveIntegerField(default=0, verbose_name='Время приготовления (в минутах)', blank=True)
    has_limit = models.BooleanField(default=False, verbose_name='Лимитированный продукт')
    limit_quantity = models.PositiveIntegerField(null=True, blank=True, verbose_name='Количество лимита')
    is_available_for_delivery = models.BooleanField(default=False, verbose_name='Доступен для доставки')
    show_in_menu = models.BooleanField(default=True, verbose_name='Показывать в меню')

    def __str__(self):
        return f"{self.product_name_rus} ({self.product_price}₪)"
    
    def get_absolute_url(self):
        return reverse('product_detail', kwargs={'pk': self.pk})


class ProductQuantityForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['quantity']


class OrderChangeLog(models.Model):
    ACTION_CHOICES = (
        ('add', 'Добавили'),
        ('decrease', 'Убавили'),
        ('delete', 'Удалили'),
        ('increase', 'Прибавили'),
    )

    order = models.ForeignKey('Order', on_delete=models.CASCADE)
    order_item = models.ForeignKey('OrderItem', on_delete=models.CASCADE, null=True, blank=True)
    product_name = models.CharField(max_length=255)
    action = models.CharField(max_length=10, choices=ACTION_CHOICES)
    change_time = models.DateTimeField(auto_now_add=True)
    changed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, verbose_name='Изменил')

    class Meta:
        ordering = ['change_time']


class ProductStock(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='stock')
    received_quantity = models.PositiveIntegerField()
    received_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.product.product_name_rus} - {self.received_quantity} received on {self.received_date}"
