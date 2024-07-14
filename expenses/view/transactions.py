from django.db import models, transaction
from django.db.models import Sum, Q
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from restaurant_app.models.orders import Order, Category, Transaction, PaymentMethod
from delivery_app.models import DeliveryOrder
from pickup_app.models import PickupOrder
from django.shortcuts import render
from django.utils import timezone
from datetime import datetime

import logging

logger = logging.getLogger(__name__)

def get_summary_data_from_order_summary(start_date, end_date):
    try:
        start_datetime = timezone.make_aware(datetime.combine(start_date or timezone.localdate(), datetime.min.time()))
        end_datetime = timezone.make_aware(datetime.combine(end_date or timezone.localdate(), datetime.max.time()))

        total_delivery_income = DeliveryOrder.objects.filter(
            delivery_date__range=(start_datetime, end_datetime),
            is_completed=True
        ).aggregate(total=Sum('total_amount'))['total'] or 0

        total_pickup_income = PickupOrder.objects.filter(
            date_created__range=(start_datetime, end_datetime),
            is_completed=True
        ).aggregate(total=Sum('total_amount'))['total'] or 0

        logger.info(f'Delivery income from {start_datetime} to {end_datetime}: {total_delivery_income}')
        logger.info(f'Pickup income from {start_datetime} to {end_datetime}: {total_pickup_income}')

        return total_delivery_income, total_pickup_income
    except Exception as e:
        logger.error(f'Error in get_summary_data_from_order_summary: {e}')
        return 0, 0

processing_order_ids = set()

@receiver(pre_save, sender=DeliveryOrder)
def check_and_set_transaction_created(sender, instance, **kwargs):
    if instance.is_completed and not instance.transaction_created:
        existing_transactions = Transaction.objects.filter(
            type=Transaction.INCOME,
            category__name='Delivery Income',
            amount=instance.total_amount,
            date=instance.delivery_date,
            payment_method__method=instance.payment_method
        )
        if existing_transactions.exists():
            instance.transaction_created = True
        logger.info(f'Pre save signal processed for DeliveryOrder {instance.id}. Is completed: {instance.is_completed}, Transaction created: {instance.transaction_created}')

@receiver(post_save, sender=DeliveryOrder)
def create_transaction_on_delivery_completion(sender, instance, **kwargs):
    if instance.id in processing_order_ids:
        logger.info(f'Skipping duplicate signal for DeliveryOrder {instance.id}')
        return

    if instance.is_completed and not instance.transaction_created:
        processing_order_ids.add(instance.id)
        try:
            with transaction.atomic():
                logger.info(f'Post save signal received for DeliveryOrder {instance.id}. Is completed: {instance.is_completed}, Transaction created: {instance.transaction_created}')

                category, _ = Category.objects.get_or_create(name='Delivery Income')

                payment_method, cash_amount, card_amount = get_payment_details(instance.payment_method, instance.total_amount)

                if instance.total_amount is None:
                    raise ValueError('Total amount for DeliveryOrder cannot be None')

                transaction, created = Transaction.objects.update_or_create(
                    type=Transaction.INCOME,
                    category=category,
                    amount=instance.total_amount,
                    cash_amount=cash_amount,
                    card_amount=card_amount,
                    payment_method=payment_method,
                    date=instance.delivery_date,
                    defaults={'category': category}
                )
                if created:
                    instance.transaction_created = True
                    instance.save(update_fields=['transaction_created'])
                    logger.info(f'Transaction created for DeliveryOrder {instance.id}: {transaction}')
                else:
                    logger.info(f'Transaction already exists for DeliveryOrder {instance.id}: {transaction}')
        except Exception as e:
            logger.error(f'Error creating transaction for DeliveryOrder {instance.id}: {e}')
        finally:
            processing_order_ids.remove(instance.id)

@receiver(post_save, sender=PickupOrder)
def create_transaction_on_pickup_completion(sender, instance, **kwargs):
    try:
        if instance.is_completed and not instance.transaction_created:
            category, _ = Category.objects.get_or_create(name='Pickup Income')

            payment_method = None
            cash_amount = None
            card_amount = None

            if instance.payment_method == 'cash':
                payment_method = PaymentMethod.objects.filter(method=PaymentMethod.CASH).first()
                cash_amount = instance.total_amount
            elif instance.payment_method == 'card':
                payment_method = PaymentMethod.objects.filter(method=PaymentMethod.CREDIT_CARD).first()
                card_amount = instance.total_amount

            if instance.total_amount is None:
                print(f'PickupOrder {instance.id} has no total amount')
                raise ValueError('Total amount for PickupOrder cannot be None')

            transaction = Transaction.objects.create(
                type=Transaction.INCOME,
                category=category,
                amount=instance.total_amount,
                cash_amount=cash_amount,
                card_amount=card_amount,
                payment_method=payment_method,
                date=instance.created_at
            )
            print(f'Transaction created: {transaction}')
            instance.transaction_created = True
            instance.save(update_fields=['transaction_created'])
        else:
            print(f'PickupOrder {instance.id} is not completed or transaction already created')
    except Exception as e:
        print(f'Error creating transaction for PickupOrder {instance.id}: {e}')


def get_payment_details(payment_method_str, total_amount):
    payment_method = None
    cash_amount = None
    card_amount = None

    if payment_method_str == 'cash':
        payment_method = PaymentMethod.objects.filter(method=PaymentMethod.CASH).first()
        cash_amount = total_amount
    elif payment_method_str in ['credit_card', 'card']:
        payment_method = PaymentMethod.objects.filter(method=PaymentMethod.CREDIT_CARD).first()
        card_amount = total_amount

    logger.info(f'Payment details: method={payment_method_str}, payment_method={payment_method}, cash_amount={cash_amount}, card_amount={card_amount}')

    return payment_method, cash_amount, card_amount


def transaction_list(request):
    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')

    start_datetime_aware = timezone.make_aware(datetime.combine(datetime.strptime(start_date_str, '%Y-%m-%d').date() if start_date_str else timezone.localdate(), datetime.min.time()))
    end_datetime_aware = timezone.make_aware(datetime.combine(datetime.strptime(end_date_str, '%Y-%m-%d').date() if end_date_str else timezone.localdate(), datetime.max.time()))

    incomes_query = Transaction.objects.filter(type=Transaction.INCOME, date__range=(start_datetime_aware, end_datetime_aware))
    expenses_query = Transaction.objects.filter(type=Transaction.EXPENSE, date__range=(start_datetime_aware, end_datetime_aware))

    total_income = incomes_query.aggregate(total=Sum('amount'))['total'] or 0
    total_expense = expenses_query.aggregate(total=Sum('amount'))['total'] or 0

    difference = total_income - total_expense
    percentage_difference = ((total_income - total_expense) / total_expense) * 100 if total_expense else 100

    category_expenses = expenses_query.values('category__name').annotate(total=Sum('amount'))
    category_names = [item['category__name'] for item in category_expenses]
    category_amounts = [float(item['total']) for item in category_expenses]

    total_amount = sum(category_amounts)
    category_percentages = [(amount / total_amount) * 100 for amount in category_amounts]
    category_names_with_percentages = [f"{name} ({percentage:.2f}%)" for name, percentage in zip(category_names, category_percentages)]

    payment_methods = PaymentMethod.objects.filter(method__in=[PaymentMethod.CASH, PaymentMethod.CREDIT_CARD, PaymentMethod.BANK_TRANSFER])
    total_cash_income = incomes_query.filter(payment_method__method=PaymentMethod.CASH).aggregate(total=Sum('cash_amount'))['total'] or 0
    total_card_income = incomes_query.filter(payment_method__method=PaymentMethod.CREDIT_CARD).aggregate(total=Sum('card_amount'))['total'] or 0
    bank_transfer_income = incomes_query.filter(payment_method__method=PaymentMethod.BANK_TRANSFER).aggregate(total=Sum('amount'))['total'] or 0

    total_delivery_income_cash = incomes_query.filter(
        Q(category__name='Delivery Income') & Q(payment_method__method=PaymentMethod.CASH)
    ).aggregate(total=Sum('cash_amount'))['total'] or 0

    total_delivery_income_card = incomes_query.filter(
        Q(category__name='Delivery Income') & Q(payment_method__method=PaymentMethod.CREDIT_CARD)
    ).aggregate(total=Sum('card_amount'))['total'] or 0

    total_delivery_income = total_delivery_income_cash + total_delivery_income_card

    total_delivery_orders = DeliveryOrder.objects.filter(
        delivery_date__range=(start_datetime_aware, end_datetime_aware),
        is_completed=True
    )
    logger.info(f"Delivery orders from {start_datetime_aware} to {end_datetime_aware}: {[order.id for order in total_delivery_orders]}")
    total_delivery_orders_count = total_delivery_orders.count()

    total_pickup_income_cash = incomes_query.filter(
        Q(category__name='Pickup Income') & Q(payment_method__method=PaymentMethod.CASH)
    ).aggregate(total=Sum('cash_amount'))['total'] or 0

    total_pickup_income_card = incomes_query.filter(
        Q(category__name='Pickup Income') & Q(payment_method__method=PaymentMethod.CREDIT_CARD)
    ).aggregate(total=Sum('card_amount'))['total'] or 0

    total_pickup_income = total_pickup_income_cash + total_pickup_income_card

    total_pickup_orders = PickupOrder.objects.filter(
        date_created__range=(start_datetime_aware, end_datetime_aware),
        is_completed=True
    )
    logger.info(f"Pickup orders from {start_datetime_aware} to {end_datetime_aware}: {[order.id for order in total_pickup_orders]}")
    total_pickup_orders_count = total_pickup_orders.count()

    table_service_income = incomes_query.filter(category__name='Table Service Income').aggregate(total=Sum('amount'))['total'] or 0
    table_service_income_cash = incomes_query.filter(Q(category__name='Table Service Income') & Q(cash_amount__isnull=False)).aggregate(total=Sum('cash_amount'))['total'] or 0
    table_service_income_card = incomes_query.filter(Q(category__name='Table Service Income') & Q(card_amount__isnull=False)).aggregate(total=Sum('card_amount'))['total'] or 0

    total_cash_expense = expenses_query.filter(payment_method__method=PaymentMethod.CASH).aggregate(total=Sum('cash_amount'))['total'] or 0
    total_card_expense = expenses_query.filter(payment_method__method=PaymentMethod.CREDIT_CARD).aggregate(total=Sum('card_amount'))['total'] or 0
    total_bank_transfer_expense = expenses_query.filter(payment_method__method=PaymentMethod.BANK_TRANSFER).aggregate(total=Sum('amount'))['total'] or 0

    payment_methods_stats = [
        {'payment_method': 'Наличные', 'total': total_cash_expense},
        {'payment_method': 'Карта', 'total': total_card_expense},
        {'payment_method': 'Банковский перевод', 'total': total_bank_transfer_expense},
    ]

    payment_methods_income_stats = [
        {'payment_method': 'Наличные', 'total': total_cash_income},
        {'payment_method': 'Карта', 'total': total_card_income},
        {'payment_method': 'Банковский перевод', 'total': bank_transfer_income},
    ]

    total_closed_tables = Order.objects.filter(created_at__range=(start_datetime_aware, end_datetime_aware), is_completed=True).count()

    logger.info(f"Total closed tables from {start_datetime_aware} to {end_datetime_aware}: {total_closed_tables}")

    return render(request, 'transaction_list.html', {
        'incomes': incomes_query,
        'expenses': expenses_query,
        'total_income': total_income,
        'total_expense': total_expense,
        'total_delivery_income': total_delivery_income,
        'total_delivery_income_cash': total_delivery_income_cash,
        'total_delivery_income_card': total_delivery_income_card,
        'total_pickup_income_cash': total_pickup_income_cash,
        'total_pickup_income_card': total_pickup_income_card,
        'total_pickup_income': total_pickup_income,
        'total_table_service_income_cash': table_service_income_cash,
        'total_table_service_income_card': table_service_income_card,
        'total_table_service_income': table_service_income,
        'difference': difference,
        'percentage_difference': percentage_difference,
        'category_names': category_names,
        'category_amounts': category_amounts,
        'category_percentages': category_percentages,
        'category_names_with_percentages': category_names_with_percentages,
        'payment_methods_stats': payment_methods_stats,
        'payment_methods_income_stats': payment_methods_income_stats,
        'start_date': start_date_str or '',
        'end_date': end_date_str or '',
        'total_closed_tables': total_closed_tables,
        'total_pickup_orders': total_pickup_orders_count,
        'total_delivery_orders': total_delivery_orders_count,
    })
