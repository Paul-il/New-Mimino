from django.db import models
from datetime import timedelta
from django.utils import timezone
from restaurant_app.models.product import Product

# Глобальные переменные для определения выборов
CITY_CHOICES = (
    ('חיפה', 'Хайфа'), 
    ('נשר', 'Нэшер'), 
    ('טירת כרמל', 'Тира'), 
    ('כפר גלים', 'Кфар Галим'),
    ('קריית חיים', 'Кирият Хаим'), 
    ('קריית אתא', 'Кирият Ата'), 
    ('קריית ביאליק', 'Кирият Биалик'),
    ('קריית ים', 'Кирият Ям'),
    ('קריית מוצקין', 'Кирият Моцкин')
)

PAYMENT_METHOD_CHOICES = (
    ('cash', 'Наличные'),
    ('credit_card', 'Кредитная карта'),
)


class DeliveryCustomer(models.Model):
    delivery_phone_number = models.CharField(max_length=10)
    name = models.CharField(max_length=30)
    city = models.CharField(max_length=50, choices=CITY_CHOICES)
    street = models.CharField(max_length=50)
    house_number = models.CharField(max_length=10)
    floor = models.CharField(max_length=10)
    apartment_number = models.CharField(max_length=10)
    intercom_code = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.name} - {self.delivery_phone_number}"


def mark_as_completed(modeladmin, request, queryset):
    week_ago = timezone.now() - timedelta(days=7)
    queryset.filter(created_at__lte=week_ago, is_completed=False).update(is_completed=True)


class DeliveryOrder(models.Model):
    customer = models.ForeignKey(DeliveryCustomer, on_delete=models.CASCADE, related_name='orders')
    courier = models.ForeignKey('Courier', on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_completed = models.BooleanField(default=False)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    delivery_date = models.DateField(null=True, blank=True)
    delivery_time = models.TimeField(null=True, blank=True)
    transaction_created = models.BooleanField(default=False)
    payment_method = models.CharField(
        max_length=12,
        choices=PAYMENT_METHOD_CHOICES,
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = 'Delivery Order'
        verbose_name_plural = 'Delivery Orders'

    def __str__(self):
        return f"{self.pk} - {self.customer.name} ({self.customer.delivery_phone_number})"


NAME_CHOICES = [
    ('solo', 'Solo'),
    ('our_courier', 'Стас'),
    # Другие имена
]    
    
class Courier(models.Model):
    name = models.CharField(max_length=50, choices=NAME_CHOICES)  
    delivery_address = models.TextField(blank=True, null=True)
    delivery_city = models.CharField(max_length=50, choices=CITY_CHOICES, blank=True, null=True)
    delivery_amount = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    payment_method = models.CharField(max_length=12, choices=PAYMENT_METHOD_CHOICES, blank=True, null=True)

    def __str__(self):
        return self.name


class CourierDelivery(models.Model):
    courier = models.ForeignKey(Courier, on_delete=models.CASCADE)
    delivery_address = models.CharField(max_length=255)
    delivery_city = models.CharField(max_length=50, choices=CITY_CHOICES)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=12, choices=PAYMENT_METHOD_CHOICES)

    def __str__(self):
        return f"{self.courier.name} - {self.delivery_city} - {self.total_price}₪"


class DeliveryProduct(models.Model):
    delivery_order = models.ForeignKey(DeliveryOrder, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True)
    quantity = models.PositiveIntegerField(default=1)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Delivery Product'
        verbose_name_plural = 'Delivery Products'

    def __str__(self):
        return f'{self.product.product_name_rus} ({self.quantity})'


class DeliveryCart(models.Model):
    delivery_order = models.ForeignKey(DeliveryOrder, on_delete=models.CASCADE, related_name='delivery_carts', null=True)
    customer = models.ForeignKey(DeliveryCustomer, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    total_price = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    is_completed = models.BooleanField(default=False)

    def get_total(self):
        if not self.pk:
            return 0
        else:
            return sum([item.quantity * item.product.product_price for item in self.delivery_cart_items.all()])

    def save(self, *args, **kwargs):
        self.total_price = self.get_total()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Cart ({self.pk}) for delivery order {self.delivery_order.customer.delivery_phone_number}"


class DeliveryCartItem(models.Model):
    cart = models.ForeignKey(DeliveryCart, on_delete=models.CASCADE, related_name='delivery_cart_items')
    delivery_order = models.ForeignKey(DeliveryOrder, on_delete=models.CASCADE, related_name='delivery_cart_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='delivery_product', null=True)
    quantity = models.PositiveIntegerField(default=1)
    printed_quantity = models.PositiveIntegerField(default=0)

    def save(self, *args, **kwargs):
        self.quantity = int(self.quantity)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.quantity} x {self.product.product_name_rus}"
