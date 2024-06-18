from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from .tables import Table
from .product import Product
from django.contrib.auth.models import User



class Order(models.Model):
    table = models.ForeignKey(Table, on_delete=models.CASCADE, related_name='orders')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="created_orders")
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    is_completed = models.BooleanField(default=False)
    comments = models.TextField(null=True, blank=True)
    last_printed_comments = models.TextField(null=True, blank=True)
    table_number = models.IntegerField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    num_of_people = models.IntegerField(default=1)
    cash_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    card_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    payment_processed = models.BooleanField(default=False)
    is_confirmed = models.BooleanField(default=False)
    is_bill_printed = models.BooleanField(default=False)
    
    class Status(models.TextChoices):
        ACTIVE = 'active', _('Active')
        COMPLETED = 'completed', _('Completed')
        CANCELED = 'canceled', _('Canceled')

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE,
    )

    class PaymentMethod(models.TextChoices):
        CASH = 'cash', _('Cash')
        CARD = 'card', _('Card')
        MIXED = 'mixed', _('Mixed')

    payment_method = models.CharField(
        max_length=10,
        choices=PaymentMethod.choices,
        null=True,
        blank=True,
    )
    
    def total_sum(self):
        return sum(item.product.product_price * item.quantity for item in self.order_items.all())

    def remaining_amount(self):
        total_paid = (self.cash_amount or 0) + (self.card_amount or 0)
        return self.total_sum() - total_paid

    def __str__(self):
        return f"Order {self.pk} ({self.table})"

    def tips_provided(self):
        return self.tips.exists()


class WaiterOrder(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='waiter_orders')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_waiter_orders')
    last_printed_comments = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_completed = models.BooleanField(default=False)

    
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_items', null=True, blank=True)
    waiter_order = models.ForeignKey(WaiterOrder, on_delete=models.CASCADE, related_name='waiter_order_items', null=True, blank=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='order_items')
    quantity = models.PositiveIntegerField(_('quantity'), default=1)
    phone_number = models.CharField(max_length=10)
    printed = models.BooleanField(default=False)
    printed_quantity = models.IntegerField(default=0)
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0.00, verbose_name='Процент скидки')
    is_delivered = models.BooleanField(default=False)

    class Meta:
        unique_together = ('order', 'product')

    @classmethod
    def remove_zero_quantity_products(cls):
        cls.objects.filter(quantity=0).delete()


class Category(models.Model):
    name = models.CharField(max_length=200)
    
    def __str__(self):
        return self.name

class PaymentMethod(models.Model):
    CASH = 'CASH'
    BANK_TRANSFER = 'BANK'
    CREDIT_CARD = 'CARD'
    MIXED = 'MIXED'
    PAYMENT_METHOD_CHOICES = [
        (CASH, 'Cash'),
        (BANK_TRANSFER, 'Bank Transfer'),
        (CREDIT_CARD, 'Card'),
        (MIXED, 'Mixed')
    ]
    
    method = models.CharField(max_length=5, choices=PAYMENT_METHOD_CHOICES)
    
    def __str__(self):
        return self.get_method_display()

class Transaction(models.Model):
    INCOME = 'IN'
    EXPENSE = 'EX'
    TRANSACTION_TYPE_CHOICES = [
        (INCOME, 'Income'),
        (EXPENSE, 'Expense'),
    ]

    type = models.CharField(max_length=2, choices=TRANSACTION_TYPE_CHOICES)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    added_date = models.DateField(auto_now_add=True)
    date = models.DateField()
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.SET_NULL, null=True, blank=True)
    cash_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    card_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return str(self.category.name)
    
def get_payment_method_from_order(order):
    if order.payment_method == Order.PaymentMethod.CASH:
        return 'Cash'
    elif order.payment_method == Order.PaymentMethod.CARD:
        return 'Card'
    elif order.payment_method == Order.PaymentMethod.MIXED:
        return 'Mixed'
    else:
        return None
