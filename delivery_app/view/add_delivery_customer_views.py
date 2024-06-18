"""
Этот модуль содержит представления для управления клиентами и заказами доставки в приложении Django.
Он включает в себя функции для добавления новых клиентов, обновления данных существующих клиентов,
а также создания и обновления заказов на доставку.
"""
# add_delivery_customer_views.py

from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.views import View

from delivery_app.forms import DeliveryCustomerForm
from delivery_app.models import DeliveryCustomer, DeliveryOrder, DeliveryCartItem


class DeliveryCustomerView(View):
    form_class = DeliveryCustomerForm
    template_name = 'add_delivery_customer.html'
    edit_template_name = 'edit_delivery_customer.html'

    def get_customer_by_phone(self, delivery_phone_number):
        return DeliveryCustomer.objects.filter(delivery_phone_number=delivery_phone_number).first()

    def handle_future_orders(self, saved_customer):
        now = timezone.localtime()
        return DeliveryOrder.objects.filter(
            customer=saved_customer,
            delivery_date__gt=now.date(),
            is_completed=False
        ).exists()

    def create_or_update_order(self, saved_customer, delivery_type, delivery_phone_number):
        now = timezone.localtime()
        if delivery_type == 'later':
            return redirect(reverse('delivery_app:view_for_later_delivery', args=[delivery_phone_number, delivery_type]))
        
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

    def get_form(self, request, customer=None):
        return self.form_class(request.POST or None, instance=customer)

    def get(self, request, delivery_phone_number, delivery_type, edit=False):
        customer = self.get_customer_by_phone(delivery_phone_number)
        form = self.get_form(request, customer)
        template = self.edit_template_name if edit else self.template_name
        return render(request, template, {
            'form': form,
            'delivery_phone_number': delivery_phone_number,
            'delivery_type': delivery_type,
            'edit': edit
        })

    def post(self, request, delivery_phone_number, delivery_type, edit=False):
        customer = self.get_customer_by_phone(delivery_phone_number)
        form = self.get_form(request, customer)
        if form.is_valid():
            saved_customer = form.save(commit=False)
            saved_customer.delivery_phone_number = delivery_phone_number
            saved_customer.save()

            # Убедитесь, что клиент сохранен перед использованием в фильтрах
            saved_customer = get_object_or_404(DeliveryCustomer, pk=saved_customer.pk)

            if self.handle_future_orders(saved_customer) and delivery_type == 'now':
                return redirect(reverse('delivery_app:view_for_later_delivery', args=[delivery_phone_number, 'later']))

            return self.create_or_update_order(saved_customer, delivery_type, delivery_phone_number)

        template = self.edit_template_name if edit else self.template_name
        return render(request, template, {
            'form': form,
            'delivery_phone_number': delivery_phone_number,
            'delivery_type': delivery_type,
            'edit': edit
        })


@login_required
def add_delivery_customer_view(request, delivery_phone_number, delivery_type):
    view = DeliveryCustomerView.as_view()
    return view(request, delivery_phone_number, delivery_type)


@login_required
def save_delivery_customer_changes_view(request, delivery_phone_number, delivery_type, edit):
    view = DeliveryCustomerView.as_view()
    return view(request, delivery_phone_number, delivery_type, edit=edit)
