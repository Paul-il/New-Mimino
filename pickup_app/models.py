from django.db import models
from django.utils import timezone
from django.db.models import Sum

from restaurant_app.models.product import Product


class PickupOrder(models.Model):
    phone = models.CharField(max_length=20)
    name = models.CharField(max_length=20)
    date_created = models.DateTimeField(auto_now_add=True, editable=False)
    date_updated = models.DateTimeField(auto_now=True, editable=False)
    is_completed = models.BooleanField(default=False)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    payment_method = models.CharField(max_length=20, blank=True, null=True)
    cart_snapshot = models.TextField(blank=True, null=True)
    
    NEW = 'new'
    PROCESSING = 'processing'
    COMPLETED = 'completed'
    CANCELED = 'canceled'

    STATUS_CHOICES = [
        (NEW, 'New'),
        (PROCESSING, 'Processing'),
        (COMPLETED, 'Completed'),
        (CANCELED, 'Canceled'),
    ]

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=NEW)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return f"{self.phone} ({self.name})"
    
    def previous_orders_total(self):
        total = PickupOrder.objects.filter(phone=self.phone, date_created__lt=self.date_created).aggregate(Sum('total_amount'))['total_amount__sum'] or 0
        return total

class Cart(models.Model):
    pickup_order = models.ForeignKey(PickupOrder, on_delete=models.CASCADE, related_name='carts')
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    total_price = models.DecimalField(max_digits=8, decimal_places=2, default=0)

    def get_total(self):
        if not self.pk:  # check if the object has been saved to the database
            return 0
        else:
            return sum([item.quantity * item.product.product_price for item in self.cart_items.all()])

    def save(self, *args, **kwargs):
        self.total_price = self.get_total()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Cart ({self.pk}) for {self.pickup_order.phone}"

class OrderItem(models.Model):
    order = models.ForeignKey(PickupOrder, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="cart_items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    printed_quantity = models.PositiveIntegerField(default=0)  # добавлено это поле

    def __str__(self):
        return f"{self.quantity} x {self.product.product_name_rus}"


