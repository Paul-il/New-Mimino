from django.shortcuts import render
from datetime import datetime, timezone
from restaurant_app.models.orders import Order
from pickup_app.models import PickupOrder, Cart
from delivery_app.models import DeliveryOrder, DeliveryCart

from django.shortcuts import render
from datetime import datetime, timezone
from restaurant_app.models.orders import Order
from pickup_app.models import PickupOrder, Cart
from delivery_app.models import DeliveryOrder, DeliveryCart

def order_summary(request):
    # Получите дату из запроса или используйте текущую дату
    selected_date_str = request.GET.get('date')
    if selected_date_str:
        selected_date = datetime.strptime(selected_date_str, '%Y-%m-%d').date()
    else:
        selected_date = datetime.now(timezone.utc).date()
    
    start_date = datetime.combine(selected_date, datetime.min.time()).replace(tzinfo=timezone.utc)
    end_date = datetime.combine(selected_date, datetime.max.time()).replace(tzinfo=timezone.utc)

    total_orders_today = Order.objects.filter(created_at__range=(start_date, end_date)).count()
    total_orders_sum = sum(order.total_sum() for order in Order.objects.filter(created_at__range=(start_date, end_date)))

    total_pickup_orders_today = PickupOrder.objects.filter(date_created__range=(start_date, end_date)).count()
    total_pickup_orders_sum = sum(order.total_amount if order.total_amount is not None else 0 for order in PickupOrder.objects.filter(date_created__range=(start_date, end_date)))

    total_delivery_orders_today = DeliveryOrder.objects.filter(created_at__range=(start_date, end_date)).count()
    total_delivery_orders_sum = sum(order.total_amount if order.total_amount is not None else 0 for order in DeliveryOrder.objects.filter(created_at__range=(start_date, end_date)))

    total_all_orders_sum = total_orders_sum + total_pickup_orders_sum + total_delivery_orders_sum
    total_all_orders_today = total_orders_today + total_pickup_orders_today + total_delivery_orders_today

    context = {
        'selected_date': selected_date,
        'total_orders_today': total_orders_today,
        'total_orders_sum': total_orders_sum,
        'total_pickup_orders_today': total_pickup_orders_today,
        'total_pickup_orders_sum': total_pickup_orders_sum,
        'total_delivery_orders_today': total_delivery_orders_today,
        'total_delivery_orders_sum': total_delivery_orders_sum,
        'total_all_orders_sum': total_all_orders_sum,
        'total_all_orders_today': total_all_orders_today
    }

    return render(request, 'order_summary.html', context)

