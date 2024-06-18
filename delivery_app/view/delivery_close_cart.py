from django.template.loader import get_template

from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect

from ..models import DeliveryOrder, Courier, DeliveryCart


@login_required
def delivery_close_cart_view(request, delivery_phone_number, order_id):
    try:
        # Получаем данные о заказе из базы данных
        delivery_order = get_object_or_404(DeliveryOrder, pk=order_id, customer__delivery_phone_number=delivery_phone_number)
        
        delivery_cart = DeliveryCart.objects.filter(delivery_order=delivery_order).first()
        if delivery_cart:
            total_amount = delivery_cart.get_total()
            delivery_order.total_amount = total_amount
            
        # Извлекаем способ оплаты и курьера из данных запроса
        payment_method = request.POST.get('payment_method')
        print(payment_method)
        selected_courier = request.POST.get('courier')
        
        # Обновляем заказ с указанием способа оплаты и помечаем его как завершенный
        delivery_order.payment_method = payment_method
        delivery_order.is_completed = True
        if selected_courier:
            courier_instance, created = Courier.objects.get_or_create(name=selected_courier)
            delivery_order.courier = courier_instance
        delivery_order.save()
        
        # Удаляем корзину
        DeliveryCart.objects.filter(delivery_order=delivery_order).delete()

        # Перенаправляем на страницу после обработки
        return redirect('ask_where')

    except Exception as e:
        # Если что-то пошло не так, возвращаем текст ошибки
        return HttpResponse(f"Произошла ошибка: {e}", content_type='text/plain', status=500)

