# check_delivery_customer_views.py

from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.contrib.auth.decorators import login_required
from ..models import DeliveryCustomer
from ..forms import DeliveryCustomerForm

@login_required
def check_delivery_customer_view(request, delivery_phone_number, delivery_type):
    customer = get_object_or_404(DeliveryCustomer, delivery_phone_number=delivery_phone_number)
    form = DeliveryCustomerForm(request.POST or None, instance=customer)

    if request.method == 'POST':
        if form.is_valid():
            updated_customer = form.save(commit=False)
            updated_customer.delivery_phone_number = delivery_phone_number
            updated_customer.save()
            # Используйте delivery_type для дальнейшей логики
            # Например, перенаправление на разные страницы в зависимости от типа доставки
            if delivery_type == 'now':
                return redirect(reverse('delivery_app:delivery_menu', args=[delivery_phone_number, 'salads']))

            elif delivery_type == 'later':
                return redirect(reverse('delivery_app:view_for_later_delivery', args=[delivery_phone_number, delivery_type]))

            else:
                # Обработка недействительного типа доставки
                return render(request, 'error_page.html', {'error_message': 'Неверный тип доставки'})
    return render(request, 'check_delivery_customer.html', {'customer': customer, 'delivery_phone_number': delivery_phone_number, 'form': form, 'delivery_type': delivery_type})
