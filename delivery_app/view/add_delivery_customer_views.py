from django.shortcuts import render, redirect, reverse
from ..forms import DeliveryCustomerForm
from ..models import DeliveryCustomer
from django.contrib.auth.decorators import login_required

@login_required
def add_delivery_customer_view(request, delivery_phone_number):
    if request.method == 'POST':
        form = DeliveryCustomerForm(request.POST)
        if form.is_valid():
            # check if a DeliveryCustomer object with the given phone number already exists
            customer_qs = DeliveryCustomer.objects.filter(delivery_phone_number=delivery_phone_number)
            if customer_qs.exists():
                # redirect to the delivery_menu view
                return redirect(reverse('delivery_app:delivery_menu', args=[delivery_phone_number, 'salads']))

            else:
                # create a new DeliveryCustomer object
                form.save()
                # redirect to the delivery_menu view
                return redirect(reverse('delivery_app:delivery_menu', args=[delivery_phone_number, 'salads']))
    else:
        form = DeliveryCustomerForm(initial={'delivery_phone_number': delivery_phone_number})
    return render(request, 'add_delivery_customer.html', {'form': form, 'delivery_phone_number': delivery_phone_number})

@login_required
def save_delivery_customer_changes_view(request, delivery_phone_number):
    if request.method == 'POST':
        form = DeliveryCustomerForm(request.POST)
        if form.is_valid():
            # Обновляем запись в базе данных или создаем новую, если она не существует
            customer, created = DeliveryCustomer.objects.update_or_create(
                delivery_phone_number=delivery_phone_number,
                defaults={
                    'name': form.cleaned_data['name'],
                    'city': form.cleaned_data['city'],
                    'street': form.cleaned_data['street'],
                    'house_number': form.cleaned_data['house_number'],
                    'floor': form.cleaned_data['floor'],
                    'apartment_number': form.cleaned_data['apartment_number'],
                    'intercom_code': form.cleaned_data['intercom_code']
                }
            )
            return redirect(reverse('delivery_app:delivery_menu', args=[delivery_phone_number, 'salads']))
        else:
            print("ERROR")

    # Если метод запроса не POST, возвращаем пользователя на страницу подтверждения заказчика
    return redirect(reverse('delivery_app:add_delivery_customer', args=[delivery_phone_number]))