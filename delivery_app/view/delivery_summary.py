from django.shortcuts import render
from django.db.models import Sum
from django.utils import timezone
from datetime import datetime

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

def delivery_summary(request):
    selected_date_str = request.GET.get('date')
    if selected_date_str:
        selected_date = datetime.strptime(selected_date_str, '%Y-%m-%d').date()
    else:
        selected_date = timezone.now().date()

    delivery_orders = DeliveryOrder.objects.filter(delivery_date=selected_date)

    # Агрегация данных по заказам
    solo_cash_orders_total = delivery_orders.filter(courier__name="solo", payment_method='cash').aggregate(total=Sum('total_amount'))['total'] or 0
    our_courier_orders = delivery_orders.filter(courier__name="our_courier")
    our_courier_cash_orders_total = our_courier_orders.filter(payment_method='cash').aggregate(total=Sum('total_amount'))['total'] or 0
    our_courier_orders_total = our_courier_orders.aggregate(total=Sum('total_amount'))['total'] or 0
    all_orders_total = delivery_orders.aggregate(total=Sum('total_amount'))['total'] or 0

    # Расчёт суммы скидок для всех заказов "Нашего Курьера"
    our_courier_discounts_total = sum([get_discount(order.customer.city) for order in our_courier_orders])

    # Вычисление суммы, которую должен вернуть "Наш Курьер" после применения скидок ко всем заказам
    our_courier_cash_orders_after_discount = our_courier_cash_orders_total - our_courier_discounts_total

    # Группировка заказов по городам и вычисление скидок
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

    # Преобразование словаря в список для шаблона
    city_order_counts = [(city, data) for city, data in city_order_data.items()]

    # Добавляем информацию в контекст для передачи в шаблон
    context = {
        'delivery_orders': delivery_orders,
        'all_orders_total': all_orders_total,
        'solo_cash_orders_total': solo_cash_orders_total,
        'our_courier_cash_orders_total': our_courier_cash_orders_total,
        'our_courier_orders_total': our_courier_orders_total,
        'our_courier_cash_orders_after_discount': our_courier_cash_orders_after_discount,
        'selected_date': selected_date,
        'city_order_counts': city_order_counts,
    }
    
    return render(request, 'delivery_summary.html', context)
