from django.db import models
from django.utils import timezone
from restaurant_app.models.tables import Table
from restaurant_app.models.product import Product
from django.contrib.auth.models import User

class StatisticsOrder(models.Model):
    table = models.ForeignKey(Table, on_delete=models.CASCADE, related_name='statistics_orders')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='statistics_orders')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    is_completed = models.BooleanField(default=False)
    comments = models.TextField(null=True, blank=True)
    last_printed_comments = models.TextField(null=True, blank=True)
    table_number = models.IntegerField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    status = models.CharField(max_length=20)
    payment_method = models.CharField(max_length=10, null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'restaurant_app_order'

class StatisticsOrderItem(models.Model):
    order = models.ForeignKey(StatisticsOrder, on_delete=models.CASCADE, related_name='statistics_order_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='statistics_order_items')
    quantity = models.PositiveIntegerField(default=1)
    phone_number = models.CharField(max_length=10)
    printed = models.BooleanField(default=False)
    printed_quantity = models.IntegerField(default=0)

    class Meta:
        managed = False
        db_table = 'restaurant_app_orderitem'
    
    def __str__(self):
        return f"OrderItem {self.pk} ({self.product})" 
    