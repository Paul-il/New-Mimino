from django.shortcuts import render
from datetime import datetime, timezone
from restaurant_app.models.orders import Order
from pickup_app.models import PickupOrder, Cart
from delivery_app.models import DeliveryOrder, DeliveryCart

def order_summary(request):
    today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = datetime.now(timezone.utc).replace(hour=23, minute=59, second=59, microsecond=999999)

    total_orders_today = Order.objects.filter(created_at__range=(today_start, today_end)).count()
    total_orders_sum = sum(order.total_sum() for order in Order.objects.filter(created_at__range=(today_start, today_end)))

    total_pickup_orders_today = PickupOrder.objects.filter(date_created__range=(today_start, today_end)).count()
    total_pickup_orders_sum = sum(cart.get_total() for cart in Cart.objects.filter(pickup_order__date_created__range=(today_start, today_end)))

    total_delivery_orders_today = DeliveryOrder.objects.filter(created_at__range=(today_start, today_end)).count()
    total_delivery_orders_sum = sum(cart.get_total() for cart in DeliveryCart.objects.filter(delivery_order__created_at__range=(today_start, today_end)))

    context = {
        'total_orders_today': total_orders_today,
        'total_orders_sum': total_orders_sum,
        'total_pickup_orders_today': total_pickup_orders_today,
        'total_pickup_orders_sum': total_pickup_orders_sum,
        'total_delivery_orders_today': total_delivery_orders_today,
        'total_delivery_orders_sum': total_delivery_orders_sum
    }

    return render(request, 'order_summary.html', context)
