import json
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.urls import reverse
from ..models import PickupOrder, Cart

@login_required
def pickup_generate_pdf_view(request, phone_number, order_id):
    try:
        order = PickupOrder.objects.get(id=order_id, phone=phone_number)
        payment_method = request.POST.get('payment_method')
        
        if payment_method:
            # Создаем снимок корзины
            cart_snapshot = [
                {
                    'product_name': item.product.product_name_rus,
                    'quantity': item.quantity,
                    'price': float(item.product.product_price),  # Преобразуем цену в число
                    'total': item.quantity * float(item.product.product_price)  # Преобразуем общую сумму в число
                }
                for cart in order.carts.all()
                for item in cart.cart_items.all()
            ]
            
            # Сохраняем снимок корзины в формате JSON
            order.cart_snapshot = json.dumps(cart_snapshot)
            order.total_amount = sum(item['total'] for item in cart_snapshot)
            order.is_completed = True
            order.status = 'completed'
            order.payment_method = payment_method
            order.save()

            # Очищаем корзину
            Cart.objects.filter(pickup_order=order).delete()

            # Перенаправляем на страницу 'ask_where'
            return redirect('ask_where')
        else:
            return JsonResponse({'message': "Ошибка: метод оплаты не указан."}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
