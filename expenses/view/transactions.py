from django.db.models import Sum, Case, When, Value, IntegerField
from django.db import models
from datetime import date, datetime, timezone
from django.utils import timezone

from django.db.models.signals import post_save
from django.dispatch import receiver
from restaurant_app.models.orders import Order, Category

from restaurant_app.models.orders import Transaction, PaymentMethod 

from django.shortcuts import render
from restaurant_app.views_folder.order_summary import get_summary_data
from pickup_app.models import PickupOrder
from delivery_app.models import DeliveryOrder

def get_summary_data_from_order_summary(start_date, end_date):
    # Если даты не предоставлены, используем текущую дату
    start_datetime = start_date if start_date else timezone.localdate()
    end_datetime = end_date if end_date else timezone.localdate()

    # Фильтрация заказов на доставку и самовывоз по датам
    total_delivery_income = DeliveryOrder.objects.filter(
        delivery_date__range=(start_datetime, end_datetime)
    ).aggregate(total=Sum('total_amount'))['total'] or 0

    total_pickup_income = PickupOrder.objects.filter(
        date_created__range=(start_datetime, end_datetime)
    ).aggregate(total=Sum('total_amount'))['total'] or 0

    return total_delivery_income, total_pickup_income


@receiver(post_save, sender=DeliveryOrder)
def create_transaction_on_delivery_completion(sender, instance, **kwargs):
    # Проверяем, что заказ завершен и дата доставки совпадает с текущей датой
    if instance.is_completed and instance.delivery_date == timezone.localdate():
        category, _ = Category.objects.get_or_create(name='Delivery Income')

        # Определение метода платежа и суммы
        payment_method = None
        cash_amount = None
        card_amount = None

        if instance.payment_method == 'cash':
            payment_method = PaymentMethod.objects.filter(method=PaymentMethod.CASH).first()
            cash_amount = instance.total_amount
        elif instance.payment_method == 'credit_card':
            payment_method = PaymentMethod.objects.filter(method=PaymentMethod.CREDIT_CARD).first()
            card_amount = instance.total_amount

        # Создание транзакции
        Transaction.objects.create(
            type=Transaction.INCOME,
            category=category,
            amount=instance.total_amount,
            cash_amount=cash_amount,
            card_amount=card_amount,
            payment_method=payment_method,
            date=instance.delivery_date  # Дата доставки из экземпляра
        )


@receiver(post_save, sender=PickupOrder)
def create_transaction_on_pickup_completion(sender, instance, **kwargs):
    if instance.is_completed:
        category, _ = Category.objects.get_or_create(name='Pickup Income')
        
        # Определение метода платежа и суммы
        payment_method = None
        cash_amount = None
        card_amount = None

        if instance.payment_method == 'cash':
            payment_method = PaymentMethod.objects.filter(method=PaymentMethod.CASH).first()
            cash_amount = instance.total_amount
        elif instance.payment_method == 'card':
            payment_method = PaymentMethod.objects.filter(method=PaymentMethod.CREDIT_CARD).first()
            card_amount = instance.total_amount

        # Создаем транзакцию
        Transaction.objects.create(
            type=Transaction.INCOME,
            category=category,
            amount=instance.total_amount,
            cash_amount=cash_amount,
            card_amount=card_amount,
            payment_method=payment_method,
            date=instance.created_at
        )



@receiver(post_save, sender=Order)
def create_transaction_on_order_completion(sender, instance, **kwargs):
    if instance.is_completed and instance.payment_processed:
        # Используем новую категорию 'Table Service Income' вместо 'Order Income'
        category, _ = Category.objects.get_or_create(name='Table Service Income')

        # Определяем метод платежа
        payment_method = None
        cash_amount = None
        card_amount = None

        if instance.payment_method == Order.PaymentMethod.CASH:
            payment_method = PaymentMethod.objects.filter(method=PaymentMethod.CASH).first()
            cash_amount = instance.total_sum()
        elif instance.payment_method == Order.PaymentMethod.CARD:
            payment_method = PaymentMethod.objects.filter(method=PaymentMethod.CREDIT_CARD).first()
            card_amount = instance.total_sum()
        elif instance.payment_method == Order.PaymentMethod.MIXED:
            payment_method = PaymentMethod.objects.filter(method=PaymentMethod.MIXED).first()
            cash_amount = instance.cash_amount
            card_amount = instance.card_amount

        # Создаем транзакцию с новой категорией
        transaction = Transaction.objects.create(
            type=Transaction.INCOME,
            category=category,
            amount=instance.total_sum(),
            cash_amount=cash_amount,
            card_amount=card_amount,
            payment_method=payment_method,
            date=instance.updated_at
        )

        # Опционально: логирование для отладки
        payment_method_name = payment_method.get_method_display() if payment_method else "Не определен"
        


def transaction_list(request):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    incomes_query = Transaction.objects.filter(type=Transaction.INCOME)
    expenses_query = Transaction.objects.filter(type=Transaction.EXPENSE)

    start_datetime = timezone.localdate()
    end_datetime = timezone.localdate()
    # Преобразование дат из строки в объект datetime
    if start_date:
        start_datetime = datetime.strptime(start_date, '%Y-%m-%d').date()
        start_datetime_aware = timezone.make_aware(datetime.combine(start_datetime, datetime.min.time()))
    else:
        start_datetime_aware = timezone.make_aware(datetime.combine(timezone.localdate(), datetime.min.time()))

    if end_date:
        end_datetime = datetime.strptime(end_date, '%Y-%m-%d').date()
        end_datetime_aware = timezone.make_aware(datetime.combine(end_datetime, datetime.max.time()))
    else:
        end_datetime_aware = timezone.make_aware(datetime.combine(timezone.localdate(), datetime.max.time()))

    # Получение данных о доходах от доставки и самовывоза
    total_delivery_income, total_pickup_income = get_summary_data_from_order_summary(start_datetime, end_datetime)

    if start_date and end_date:
        incomes = incomes_query.filter(date__range=(start_date, end_date))
        expenses = expenses_query.filter(date__range=(start_date, end_date))
    else:
        incomes = incomes_query.all()
        expenses = expenses_query.all()
    
    # Используем агрегацию для суммирования
    total_income = incomes.aggregate(total=models.Sum('amount'))['total'] or 0
    total_expense = expenses.aggregate(total=models.Sum('amount'))['total'] or 0

    difference = total_income - total_expense
    percentage_difference = ((total_income - total_expense) / total_expense) * 100 if total_expense else 100

    category_expenses = expenses.values('category__name').annotate(total=models.Sum('amount'))
    category_names = [item['category__name'] for item in category_expenses]
    category_amounts = [float(item['total']) for item in category_expenses]

    total_amount = sum(category_amounts)
    category_percentages = [(amount / total_amount) * 100 for amount in category_amounts]
    category_names_with_percentages = [f"{name} ({percentage:.2f}%)" for name, percentage in zip(category_names, category_percentages)]

    cash_method = PaymentMethod.objects.filter(method=PaymentMethod.CASH).first()
    card_method = PaymentMethod.objects.filter(method=PaymentMethod.CREDIT_CARD).first()
    bank_transfer_method = PaymentMethod.objects.filter(method=PaymentMethod.BANK_TRANSFER).first()

    cash_amount = expenses.filter(payment_method=cash_method).aggregate(total=models.Sum('amount'))['total'] or 0 if cash_method else 0
    card_amount = expenses.filter(payment_method=card_method).aggregate(total=models.Sum('amount'))['total'] or 0 if card_method else 0
    bank_transfer_amount = expenses.filter(payment_method=bank_transfer_method).aggregate(total=models.Sum('amount'))['total'] or 0 if bank_transfer_method else 0

    # Агрегация для сумм наличных и карты
    total_cash_income = incomes.filter(models.Q(payment_method__method='CASH') | models.Q(payment_method__method='MIXED')).aggregate(total=models.Sum('cash_amount'))['total'] or 0
    total_card_income = incomes.filter(models.Q(payment_method__method='CARD') | models.Q(payment_method__method='MIXED')).aggregate(total=models.Sum('card_amount'))['total'] or 0


    bank_transfer_income = incomes.filter(payment_method=bank_transfer_method).aggregate(total=models.Sum('amount'))['total'] or 0 if bank_transfer_method else 0

    cash_method = PaymentMethod.objects.filter(method=PaymentMethod.CASH).first()
    card_method = PaymentMethod.objects.filter(method=PaymentMethod.CREDIT_CARD).first()
    mixed_method = PaymentMethod.objects.filter(method=PaymentMethod.MIXED).first()

    total_cash_income = incomes.annotate(
        cash_income=Case(
            When(payment_method=cash_method, then='amount'),
            When(payment_method=mixed_method, then='cash_amount'),
            default=Value(0),
            output_field=IntegerField()
        )
    ).aggregate(total=Sum('cash_income'))['total'] or 0

    # Агрегация для карты
    total_card_income = incomes.annotate(
        card_income=Case(
            When(payment_method=card_method, then='amount'),
            When(payment_method=mixed_method, then='card_amount'),
            default=Value(0),
            output_field=IntegerField()
        )
    ).aggregate(total=Sum('card_income'))['total'] or 0

    delivery_income_cash = 0
    delivery_income_card = 1

    selected_date = request.GET.get('selected_date')

    if selected_date:
        selected_datetime = datetime.strptime(selected_date, '%Y-%m-%d').date()
        selected_datetime_aware = timezone.make_aware(datetime.combine(selected_datetime, datetime.min.time()))

        # Пример запроса для расчета дохода от доставки с разбивкой по методам оплаты
        delivery_income_cash = DeliveryOrder.objects.filter(
            delivery_date__range=(start_datetime, end_datetime), 
            payment_method='cash'
        ).aggregate(total=Sum('total_amount'))['total'] or 0

        delivery_income_card = DeliveryOrder.objects.filter(
            delivery_date__range=(start_datetime, end_datetime), 
            payment_method='credit_card'
        ).aggregate(total=Sum('total_amount'))['total'] or 0


    else:
        # Фильтрация заказов на доставку и самовывоз по датам
        total_delivery_income = DeliveryOrder.objects.filter(
            delivery_date__range=(start_datetime, end_datetime)
        ).aggregate(total=Sum('total_amount'))['total'] or 0

        total_pickup_income = PickupOrder.objects.filter(
            date_created__range=(start_datetime, end_datetime)
        ).aggregate(total=Sum('total_amount'))['total'] or 0

    # Использование осведомленных дат в запросах
    pickup_income_cash = PickupOrder.objects.filter(
        date_created__range=(start_datetime_aware, end_datetime_aware), 
        payment_method='cash'
    ).aggregate(total=Sum('total_amount'))['total'] or 0

    pickup_income_card = PickupOrder.objects.filter(
        date_created__range=(start_datetime_aware, end_datetime_aware), 
        payment_method='card'
    ).aggregate(total=Sum('total_amount'))['total'] or 0

    table_service_income = Transaction.objects.filter(
    type=Transaction.INCOME, 
    category__name='Table Service Income', 
    date__range=(start_datetime_aware, end_datetime_aware)
    ).aggregate(total=Sum('amount'))['total'] or 0

    table_service_income_cash = Transaction.objects.filter(
    type=Transaction.INCOME, 
    category__name='Table Service Income', 
    date__range=(start_datetime_aware, end_datetime_aware),
    payment_method__method=PaymentMethod.CASH
    ).aggregate(total=Sum('cash_amount'))['total'] or 0

    table_service_income_card = Transaction.objects.filter(
        type=Transaction.INCOME, 
        category__name='Table Service Income', 
        date__range=(start_datetime_aware, end_datetime_aware),
        payment_method__method=PaymentMethod.CREDIT_CARD
    ).aggregate(total=Sum('card_amount'))['total'] or 0


    payment_methods_stats = [
        {'payment_method': 'Наличные', 'total': cash_amount},
        {'payment_method': 'Карта', 'total': card_amount},
        {'payment_method': 'Банковский перевод', 'total': bank_transfer_amount},
    ]

    payment_methods_income_stats = [
        {'payment_method': 'Наличные', 'total': total_cash_income},
        {'payment_method': 'Карта', 'total': total_card_income},
        {'payment_method': 'Банковский перевод', 'total': bank_transfer_income},
    ]
    # Прибавляем доходы от доставки и самовывоза к общему доходу
    
    return render(request, 'transaction_list.html', {
        'incomes': incomes,
        'expenses': expenses,
        'total_income': total_income,
        'total_expense': total_expense,
        'total_delivery_income': total_delivery_income,
        'total_delivery_income_cash': delivery_income_cash,
        'total_delivery_income_card': delivery_income_card,
        'total_pickup_income_cash': pickup_income_cash,
        'total_pickup_income_card': pickup_income_card,
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
        'start_date': start_date or '',
        'end_date': end_date or '',
    })