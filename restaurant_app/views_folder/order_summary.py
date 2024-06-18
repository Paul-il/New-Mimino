from django.shortcuts import render
from datetime import date, datetime
from django.utils import timezone
from restaurant_app.models.orders import Order
from pickup_app.models import PickupOrder
from delivery_app.models import DeliveryOrder

def get_summary_data(model, start_date, end_date, total_amount_attr="total_sum"):
    # Преобразование start_date и end_date в осведомлённые объекты datetime
    aware_start_date = timezone.make_aware(datetime.combine(start_date, datetime.min.time()))
    aware_end_date = timezone.make_aware(datetime.combine(end_date, datetime.max.time()))

    count = model.objects.filter(created_at__range=(aware_start_date, aware_end_date)).count()
    total_sum = sum(getattr(order, total_amount_attr)() if callable(getattr(order, total_amount_attr)) else getattr(order, total_amount_attr) or 0 
                    for order in model.objects.filter(created_at__range=(aware_start_date, aware_end_date)))
    return count, total_sum

def order_summary(request):
    selected_date_str = request.GET.get('date')
    selected_date = datetime.strptime(selected_date_str, '%Y-%m-%d').date() if selected_date_str else date.today()
    
    start_date = timezone.make_aware(datetime.combine(selected_date, datetime.min.time()))
    end_date = timezone.make_aware(datetime.combine(selected_date, datetime.max.time()))


    total_orders_today, total_orders_sum = get_summary_data(Order, start_date, end_date)
    total_pickup_orders_today, total_pickup_orders_sum = get_summary_data(PickupOrder, start_date, end_date, "total_amount")
    total_delivery_orders_today, total_delivery_orders_sum = get_summary_data(DeliveryOrder, start_date, end_date, "total_amount")

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
