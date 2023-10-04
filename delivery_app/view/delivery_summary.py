from django.shortcuts import render
from django.db.models.functions import TruncDate
from django.db.models import Sum, F, Value, Case, When, DecimalField
from django.utils import timezone

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
    # Получаем дату из GET-запроса, если она указана. В противном случае используем текущую дату.
    selected_date = request.GET.get('date', timezone.now().date())
    
    delivery_orders = DeliveryOrder.objects.annotate(
        order_date=TruncDate('created_at'),
        discount=Case(
            When(courier__name="solo", then=Value(0)),
            When(customer__city='חיפה', then=Value(25)),
            When(customer__city__icontains='קריית', then=Value(45)),
            When(customer__city='נשר', then=Value(35)),
            When(customer__city='טירת כרמל', then=Value(35)),
            default=Value(0),
            output_field=DecimalField()
        )
    ).filter(order_date=selected_date)
    
    solo_cash_orders_total = delivery_orders.filter(payment_method='cash', courier__name="solo").aggregate(total=Sum('total_amount'))['total'] or 0
    solo_cash_orders_discounted_value = delivery_orders.filter(payment_method='cash', courier__name="solo").aggregate(
        total=Sum(F('total_amount') - F('discount'))
    )['total']
    solo_cash_orders_discounted_total = solo_cash_orders_discounted_value if solo_cash_orders_discounted_value is not None else 0

    our_courier_orders_total = delivery_orders.exclude(courier__name="solo").aggregate(total=Sum('total_amount'))['total'] or 0
    our_courier_orders_discount_value = delivery_orders.exclude(courier__name="solo").aggregate(total=Sum('discount'))['total']
    our_courier_orders_discount = our_courier_orders_discount_value if our_courier_orders_discount_value is not None else 0

    our_courier_orders_discounted_total = our_courier_orders_total - our_courier_orders_discount

    all_orders_total = delivery_orders.aggregate(total=Sum('total_amount'))['total'] or 0

    context = {
        'delivery_orders': delivery_orders,
        'all_orders_total': all_orders_total,
        'solo_cash_orders_total': solo_cash_orders_total,
        'solo_cash_orders_discounted_total': solo_cash_orders_discounted_total,
        'our_courier_orders_total': our_courier_orders_total,
        'our_courier_orders_discounted_total': our_courier_orders_discounted_total,
        'selected_date': selected_date  # передаем выбранную дату в контекст
    }
    return render(request, 'delivery_summary.html', context)
