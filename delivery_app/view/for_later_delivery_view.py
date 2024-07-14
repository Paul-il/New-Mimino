# for_later_delivery_view.py
from django.shortcuts import render, redirect, reverse
from django.contrib.auth.decorators import login_required
from ..models import DeliveryCustomer, DeliveryOrder
from ..forms import DeliveryDateTimeForm, SelectOrderForm
from datetime import datetime

@login_required
def view_for_later_delivery(request, delivery_phone_number, delivery_type):
    print(delivery_type)
    customer = DeliveryCustomer.objects.get(delivery_phone_number=delivery_phone_number)
    active_orders = DeliveryOrder.objects.filter(customer=customer, is_completed=False)

    select_order_form = SelectOrderForm(request.POST or None, orders=active_orders)
    date_time_form = DeliveryDateTimeForm(request.POST or None)

    if request.method == 'POST':
        if 'select_order' in request.POST and select_order_form.is_valid():
            # Обработка SelectOrderForm
            print("Обработка SelectOrderForm")
            selected_order = select_order_form.cleaned_data['order']
            # Перенаправление на страницу подтверждения заказа или другую страницу
            return redirect(reverse('delivery_app:delivery_menu', args=[delivery_phone_number, 'salads', delivery_type]))

        elif 'delivery_date_time' in request.POST and date_time_form.is_valid():
            # Обработка DeliveryDateTimeForm
            print("Обработка DeliveryDateTimeForm")
            delivery_date = date_time_form.cleaned_data['date']
            delivery_time = date_time_form.cleaned_data['time']
            print(delivery_date, delivery_time)
            # Создание нового заказа
            new_order = DeliveryOrder.objects.create(
                customer=customer,
                delivery_date=delivery_date,
                delivery_time=delivery_time,
                is_completed=False
            )
            # Перенаправление на страницу подтверждения заказа или другую страницу
            return redirect(reverse('delivery_app:delivery_menu', args=[delivery_phone_number, 'salads', delivery_type]))
            
    context = {
        'customer': customer,
        'select_order_form': select_order_form if active_orders.exists() else None,
        'date_time_form': date_time_form if not active_orders.exists() else None,
        'delivery_type': delivery_type
    }

    return render(request, 'later_delivery.html', context)
