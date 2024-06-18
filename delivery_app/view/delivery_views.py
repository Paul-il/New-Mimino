from django.shortcuts import render, redirect, reverse
from django.contrib.auth.decorators import login_required
from ..forms import DeliveryForm
from ..models import DeliveryCustomer

@login_required
def delivery_view(request, delivery_type):
    if request.method == 'POST':
        form = DeliveryForm(request.POST)
        if form.is_valid():
            delivery_phone_number = form.cleaned_data['delivery_phone_number']
            if DeliveryCustomer.objects.filter(delivery_phone_number=delivery_phone_number).exists():
                # Перенаправляем пользователя на страницу проверки клиента с типом доставки
                return redirect(reverse('delivery_app:check_delivery_customer', args=[delivery_phone_number, delivery_type]))
            else:
                # Перенаправляем пользователя на страницу добавления клиента с типом доставки
                return redirect(reverse('delivery_app:add_delivery_customer', args=[delivery_phone_number, delivery_type]))
    else:
        form = DeliveryForm()
    return render(request, 'check_delivery_number.html', {'form': form, 'delivery_type': delivery_type})
