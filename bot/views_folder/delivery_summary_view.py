from datetime import datetime
from django.utils import timezone
from django.db.models import Sum
from rest_framework.decorators import api_view
from rest_framework.response import Response
from ..models import DeliveryOrder

def get_discount(city_name):
    if city_name == 'חיפה':
        return 25
    elif 'קריית' in city_name:
        return 45
    elif city_name == 'נשר':
        return 35
    elif city_name == 'טירת כרמל':
        return 35
    else:
        return 0

@api_view(['GET'])
def api_delivery_summary(request):
    selected_date_str = request.GET.get('date')
    if selected_date_str:
        selected_date = datetime.strptime(selected_date_str, '%Y-%m-%d').date()
    else:
        selected_date = timezone.now().date()

    delivery_orders = DeliveryOrder.objects.filter(delivery_date=selected_date)

    solo_cash_orders_total = delivery_orders.filter(courier__name="solo", payment_method='cash').aggregate(total=Sum('total_amount'))['total'] or 0
    our_courier_orders = delivery_orders.filter(courier__name="our_courier")
    our_courier_cash_orders_total = our_courier_orders.filter(payment_method='cash').aggregate(total=Sum('total_amount'))['total'] or 0
    our_courier_orders_total = our_courier_orders.aggregate(total=Sum('total_amount'))['total'] or 0
    all_orders_total = delivery_orders.aggregate(total=Sum('total_amount'))['total'] or 0

    our_courier_discounts_total = sum([get_discount(order.customer.city) for order in our_courier_orders])
    our_courier_cash_orders_after_discount = our_courier_cash_orders_total - our_courier_discounts_total

    city_order_data = {}
    for order in delivery_orders:
        if order.courier and order.courier.name == "solo":
            continue

        city = order.customer.city
        discount_amount = get_discount(city)

        if discount_amount == 45:
            grouped_city = 'קריות'
            city_order_data.setdefault(grouped_city, {'total_orders': 0, 'total_discount_amount': 0})
            city_order_data[grouped_city]['total_orders'] += 1
            city_order_data[grouped_city]['total_discount_amount'] += discount_amount
        else:
            city_order_data.setdefault(city, {'total_orders': 0, 'total_discount_amount': 0})
            city_order_data[city]['total_orders'] += 1
            city_order_data[city]['total_discount_amount'] += discount_amount

    city_order_counts = [(city, data) for city, data in city_order_data.items()]

    data = {
        'delivery_orders': delivery_orders.values(),
        'all_orders_total': all_orders_total,
        'solo_cash_orders_total': solo_cash_orders_total,
        'our_courier_cash_orders_total': our_courier_cash_orders_total,
        'our_courier_orders_total': our_courier_orders_total,
        'our_courier_cash_orders_after_discount': our_courier_cash_orders_after_discount,
        'selected_date': selected_date,
        'city_order_counts': city_order_counts,
    }

    return Response(data)
