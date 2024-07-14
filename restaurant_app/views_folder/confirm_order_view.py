from django.http import JsonResponse
from restaurant_app.models.orders import Order

def confirm_order(request, order_id):
    if request.method == 'POST':
        try:
            order = Order.objects.get(id=order_id)
            order.is_confirmed = True
            order.save()
            return JsonResponse({'status': 'success', 'message': 'Заказ подтвержден'})
        except Order.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Заказ не найден'}, status=404)
