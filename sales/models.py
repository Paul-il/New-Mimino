from django.db import models
from restaurant_app.models.orders import Order, OrderItem   

class Sale(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    sale_date = models.DateTimeField(auto_now_add=True)

class SaleItem(models.Model):
    order_item = models.OneToOneField(OrderItem, on_delete=models.CASCADE)
    sale_date = models.DateTimeField(auto_now_add=True)