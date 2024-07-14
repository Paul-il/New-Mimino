from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from .tables import Table
from .product import Product
from django.contrib.auth.models import User
from django.urls import reverse
from django.conf import settings
from django.db.models import Sum, F
from decimal import Decimal


class Order(models.Model):
    table = models.ForeignKey(Table, on_delete=models.CASCADE, related_name='orders')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    is_completed = models.BooleanField(default=False)
    comments = models.TextField(null=True, blank=True)
    last_printed_comments = models.TextField(null=True, blank=True)
    table_number = models.CharField(max_length=255)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    num_of_people = models.IntegerField(default=1)
    cash_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    card_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    payment_processed = models.BooleanField(default=False)
    is_confirmed = models.BooleanField(default=False)
    is_bill_printed = models.BooleanField(default=False)
    transaction_created = models.BooleanField(default=False)

    STATUS_CHOICES = [
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('canceled', 'Canceled'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')

    PAYMENT_METHOD_CHOICES = [
        ('cash', 'Cash'),
        ('card', 'Card'),
        ('mixed', 'Mixed'),
    ]
    payment_method = models.CharField(max_length=10, choices=PAYMENT_METHOD_CHOICES, null=True, blank=True)

    def total_sum(self):
        """Calculate the total sum of the order."""
        total = self.order_items.aggregate(total=Sum(F('product__product_price') * F('quantity')))['total']
        return total or Decimal('0')

    def save(self, *args, **kwargs):
        # Calculate total_price only if the order instance has a primary key
        if self.pk:
            self.total_price = self.calculate_total_price()
        super().save(*args, **kwargs)

    def calculate_total_price(self):
        total_price = self.order_items.aggregate(
            total=Sum(F('product__product_price') * F('quantity'))
        )['total']
        return total_price or 0

    def __str__(self):
        return f"Order {self.pk} ({self.table})"

    def get_total_amount(self):
        """Alias for total_sum method to avoid changing existing code."""
        return self.total_sum()

    def remaining_amount(self):
        """Calculate the remaining amount to be paid."""
        total_paid = self.cash_amount + self.card_amount
        return self.total_sum() - total_paid

    def tips_provided(self):
        """Check if tips have been provided."""
        return self.tips.exists()

    def get_absolute_url(self):
        return reverse('cart_detail', args=[str(self.id)])

    def create_transaction(self):
        """Create a transaction if the order is completed and no transaction has been created yet."""
        if self.is_completed and not self.transaction_created:
            try:
                category, _ = Category.objects.get_or_create(name='Table Service Income')

                payment_method = None
                cash_amount = None
                card_amount = None

                if self.payment_method == 'cash':
                    payment_method = PaymentMethod.objects.filter(method=PaymentMethod.CASH).first()
                    cash_amount = self.total_sum()
                elif self.payment_method == 'card':
                    payment_method = PaymentMethod.objects.filter(method=PaymentMethod.CREDIT_CARD).first()
                    card_amount = self.total_sum()
                elif self.payment_method == 'mixed':
                    payment_method = PaymentMethod.objects.filter(method=PaymentMethod.MIXED).first()
                    cash_amount = self.cash_amount
                    card_amount = self.card_amount

                total_sum = self.total_sum()
                if total_sum is None:
                    raise ValueError('Total amount for Order cannot be None')

                Transaction.objects.create(
                    type=Transaction.INCOME,
                    category=category,
                    amount=total_sum,
                    cash_amount=cash_amount,
                    card_amount=card_amount,
                    payment_method=payment_method,
                    date=self.updated_at
                )
                self.transaction_created = True
                self.save(update_fields=['transaction_created'])
            except Exception as e:
                print(f'Error creating transaction for Order {self.id}: {e}')
                raise

class WaiterOrder(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='waiter_orders')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_waiter_orders')
    last_printed_comments = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_completed = models.BooleanField(default=False)

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_items', null=True, blank=True)
    waiter_order = models.ForeignKey('WaiterOrder', on_delete=models.CASCADE, related_name='waiter_order_items', null=True, blank=True)
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
        """Remove products with zero quantity."""
        cls.objects.filter(quantity=0).delete()

    def save(self, *args, **kwargs):
        is_new = self.pk is None

        if is_new:
            if self.product.has_limit:
                if self.product.limit_quantity >= self.quantity:
                    self.product.limit_quantity = max(0, self.product.limit_quantity - self.quantity)
                    if self.product.limit_quantity == 0:
                        self.product.is_available = False
                    self.product.save()
                else:
                    raise ValueError('Not enough quantity available in the limit')
        else:
            old_quantity = OrderItem.objects.get(pk=self.pk).quantity
            quantity_difference = self.quantity - old_quantity
            if self.product.has_limit:
                if self.product.limit_quantity + old_quantity >= self.quantity:
                    self.product.limit_quantity = max(0, self.product.limit_quantity - quantity_difference)
                    if self.product.limit_quantity == 0:
                        self.product.is_available = False
                    self.product.save()
                else:
                    raise ValueError('Not enough quantity available in the limit')
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if not self.is_delivered and self.product.has_limit:
            self.product.limit_quantity += self.quantity
            if self.product.limit_quantity > 0:
                self.product.is_available = True
            self.product.save()
        super().delete(*args, **kwargs)

    def mark_delivered(self):
        """Mark the item as delivered."""
        self.is_delivered = True
        self.save()

    def unmark_delivered(self):
        """Unmark the item as delivered."""
        self.is_delivered = False
        self.save()

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

class DeliveryOrder(models.Model):
    is_completed = models.BooleanField(default=False)
    transaction_created = models.BooleanField(default=False)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    delivery_date = models.DateField()
    payment_method = models.CharField(max_length=20)

    def create_transaction(self):
        """Create a transaction if the delivery order is completed and no transaction has been created yet."""
        if self.is_completed and not self.transaction_created:
            try:
                category, _ = Category.objects.get_or_create(name='Delivery Income')

                payment_method = None
                cash_amount = None
                card_amount = None

                if self.payment_method == 'cash':
                    payment_method = PaymentMethod.objects.filter(method=PaymentMethod.CASH).first()
                    cash_amount = self.total_amount
                elif self.payment_method == 'credit_card':
                    payment_method = PaymentMethod.objects.filter(method=PaymentMethod.CREDIT_CARD).first()
                    card_amount = self.total_amount

                if self.total_amount is None:
                    raise ValueError('Total amount for DeliveryOrder cannot be None')

                Transaction.objects.create(
                    type=Transaction.INCOME,
                    category=category,
                    amount=self.total_amount,
                    cash_amount=cash_amount,
                    card_amount=card_amount,
                    payment_method=payment_method,
                    date=self.delivery_date
                )
                self.transaction_created = True
                self.save(update_fields=['transaction_created'])
            except Exception as e:
                print(f'Error creating transaction for DeliveryOrder {self.id}: {e}')
                raise

def get_payment_method_from_order(order):
    """Get the payment method for a given order."""
    payment_methods = {
        Order.PAYMENT_METHOD_CHOICES[0][0]: 'Cash',
        Order.PAYMENT_METHOD_CHOICES[1][0]: 'Card',
        Order.PAYMENT_METHOD_CHOICES[2][0]: 'Mixed'
    }
    return payment_methods.get(order.payment_method)
