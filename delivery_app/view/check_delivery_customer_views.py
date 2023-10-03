from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.contrib.auth.decorators import login_required
from ..models import DeliveryCustomer
from ..forms import DeliveryCustomerForm

@login_required
def check_delivery_customer_view(request, delivery_phone_number):
    customer = get_object_or_404(DeliveryCustomer, delivery_phone_number=delivery_phone_number)
    form = DeliveryCustomerForm(request.POST or None, instance=customer)

    if request.method == 'POST':
        if form.is_valid():
            updated_customer = form.save(commit=False)
            updated_customer.delivery_phone_number = delivery_phone_number
            print(updated_customer)
            updated_customer.save()
            return redirect(reverse('delivery_app:delivery_menu', args=[delivery_phone_number, 'salads']))
    return render(request, 'check_delivery_customer.html', {'customer': customer, 'delivery_phone_number': delivery_phone_number, 'form': form})

