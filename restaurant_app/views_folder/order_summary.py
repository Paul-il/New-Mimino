from django.shortcuts import render
from datetime import datetime, date
from django.utils import timezone
from django.db.models import Sum
from restaurant_app.models.orders import Order
from pickup_app.models import PickupOrder
from delivery_app.models import DeliveryOrder

def get_summary_data(model, start_date, end_date, total_amount_attr):
    aware_start_date = timezone.make_aware(datetime.combine(start_date, datetime.min.time()))
    aware_end_date = timezone.make_aware(datetime.combine(end_date, datetime.max.time()))

    queryset = model.objects.filter(created_at__range=(aware_start_date, aware_end_date))

    # Debugging to see queryset results
    print(f"Queryset for {model.__name__}: {list(queryset)}")

    count = queryset.count()
    total_sum = queryset.aggregate(total_sum=Sum(total_amount_attr))['total_sum'] or 0

    # Debugging to see calculated sum
    print(f"Model: {model.__name__}, Count: {count}, Total Sum: {total_sum}")

    return count, total_sum

def order_summary(request):
    selected_date_str = request.GET.get('date')
    selected_date = datetime.strptime(selected_date_str, '%Y-%m-%d').date() if selected_date_str else date.today()
    
    start_date = selected_date
    end_date = selected_date

    total_orders_today, total_orders_sum = get_summary_data(Order, start_date, end_date, "total_price")
    total_pickup_orders_today, total_pickup_orders_sum = get_summary_data(PickupOrder, start_date, end_date, "total_amount")
    total_delivery_orders_today, total_delivery_orders_sum = get_summary_data(DeliveryOrder, start_date, end_date, "total_amount")

    total_all_orders_sum = total_orders_sum + total_pickup_orders_sum + total_delivery_orders_sum
    total_all_orders_today = total_orders_today + total_pickup_orders_today + total_delivery_orders_today

    # Debugging to see summary results
    print(f"Total Orders Today: {total_orders_today}, Total Orders Sum: {total_orders_sum}")
    print(f"Total Pickup Orders Today: {total_pickup_orders_today}, Total Pickup Orders Sum: {total_pickup_orders_sum}")
    print(f"Total Delivery Orders Today: {total_delivery_orders_today}, Total Delivery Orders Sum: {total_delivery_orders_sum}")
    print(f"Total All Orders Today: {total_all_orders_today}, Total All Orders Sum: {total_all_orders_sum}")

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
