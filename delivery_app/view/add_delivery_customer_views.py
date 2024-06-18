"""
Этот модуль содержит представления для управления клиентами и заказами доставки в приложении Django.
Он включает в себя функции для добавления новых клиентов, обновления данных существующих клиентов,
а также создания и обновления заказов на доставку.
"""
# add_delivery_customer_views.py

from django.shortcuts import render, redirect, reverse
from django.utils import timezone
from django.contrib.auth.decorators import login_required

from delivery_app.forms import DeliveryCustomerForm
from delivery_app.models import DeliveryCustomer, DeliveryOrder

@login_required
def add_delivery_customer_view(request, delivery_phone_number, delivery_type):
    # Проверка существования клиента
    customer_qs = DeliveryCustomer.objects.filter(delivery_phone_number=delivery_phone_number)
    customer = customer_qs.first() if customer_qs.exists() else None

    # Инициализация формы данными существующего клиента или пустой формой
    if customer:
        form = DeliveryCustomerForm(request.POST or None, instance=customer)
    else:
        form = DeliveryCustomerForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        # Обработка формы и создание/обновление клиента
        saved_customer = form.save(commit=False)
        saved_customer.delivery_phone_number = delivery_phone_number
        saved_customer.save()

        now = timezone.localtime()

        # Проверка на существующие заказы на будущее
        future_orders_exist = DeliveryOrder.objects.filter(
            customer=saved_customer,
            delivery_date__gt=now.date(),
            is_completed=False
        ).exists()

        if future_orders_exist and delivery_type == 'now':
            # Перенаправление на страницу с будущими заказами
            return redirect(reverse('delivery_app:view_for_later_delivery', args=[delivery_phone_number, 'later']))

        # Создание или обновление заказа
        if delivery_type == 'later':
            return redirect(reverse('delivery_app:view_for_later_delivery', args=[delivery_phone_number, delivery_type]))
        else:
            existing_order = DeliveryOrder.objects.filter(
                customer=saved_customer,
                created_at__date=now.date()
            ).first()

            if existing_order and not existing_order.is_completed:
                existing_order.delivery_date = now.date()
                existing_order.delivery_time = now.time()
                existing_order.save()
            else:
                DeliveryOrder.objects.create(
                    customer=saved_customer,
                    delivery_date=now.date(),
                    delivery_time=now.time(),
                    is_completed=False
                )

            return redirect(reverse('delivery_app:delivery_menu', args=[delivery_phone_number, 'salads', delivery_type]))

    return render(request, 'add_delivery_customer.html', {
        'form': form,
        'delivery_phone_number': delivery_phone_number,
        'delivery_type': delivery_type
    })



@login_required
def save_delivery_customer_changes_view(request, delivery_phone_number, delivery_type):
    """
    Обновляет данные клиента доставки и создает или обновляет заказ на доставку.

    Args:
        request: HttpRequest объект.
        delivery_phone_number: Телефонный номер клиента.
        delivery_type: Тип доставки ('now' или 'later').

    Returns:
        HttpResponse объект, перенаправляющий пользователя на соответствующую страницу.
    """
    try:
        customer = DeliveryCustomer.objects.get(delivery_phone_number=delivery_phone_number)
    except DeliveryCustomer.DoesNotExist:
        customer = None

    if request.method == 'POST':
        form = DeliveryCustomerForm(request.POST, instance=customer)
        if form.is_valid():
            updated_customer = form.save(commit=False)
            updated_customer.delivery_phone_number = delivery_phone_number
            updated_customer.save()
            now = timezone.localtime()

            if delivery_type == 'later':
                return redirect(reverse('delivery_app:view_for_later_delivery', args=[delivery_phone_number, delivery_type]))
            else:
                DeliveryOrder.objects.update_or_create(
                    customer=updated_customer,
                    created_at__date=now.date(),
                    defaults={
                        'delivery_date': now.date(),
                        'delivery_time': now.time(),
                        'is_completed': False
                    }
                )
                return redirect(reverse('delivery_app:delivery_menu', args=[delivery_phone_number, 'salads', delivery_type]))
    else:
        form = DeliveryCustomerForm(instance=customer)

    return render(request, 'edit_delivery_customer.html', {
        'form': form,
        'delivery_phone_number': delivery_phone_number,
        'delivery_type': delivery_type
    })