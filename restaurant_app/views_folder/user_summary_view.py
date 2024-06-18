from django.shortcuts import render, get_object_or_404
from django.contrib.auth.models import User
from ..models.tables import TipDistribution
from ..models.orders import Order, OrderItem
from django.db.models import Sum, F
from django.utils import timezone
from django.utils.timezone import localtime
import random
import json
from django.contrib.auth.decorators import login_required
import decimal
import calendar

class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, decimal.Decimal):
            return float(obj)
        return super(DecimalEncoder, self).default(obj)

def calculate_totals(user, orders):
    total_order_amount = OrderItem.objects.filter(order__in=orders).aggregate(total=Sum(F('quantity') * F('product__product_price')))['total'] or 0
    total_tips = TipDistribution.objects.filter(user=user, tip__order__in=orders).aggregate(Sum('amount'))['amount__sum'] or 0
    tip_ratio = round((total_tips / total_order_amount) * 100, 1) if total_order_amount > 0 else 0

    print(f"Общая сумма заказов: {total_order_amount}")
    print(f"Общая сумма чаевых: {total_tips}")
    print(f"Соотношение чаевых к заказам: {tip_ratio}%")
    print(f"Количество заказов: {orders.count()}")
    print(f"Пользователь: {user.username}")

    return total_order_amount, total_tips, tip_ratio

@login_required
def user_summary(request):
    today = localtime(timezone.now()).date()
    first_day_of_current_month = today.replace(day=1)

    print(f"Сегодня: {today}, Первый день текущего месяца: {first_day_of_current_month}")

    users = User.objects.all().prefetch_related('bookings').select_related('userprofile', 'tipgoal')

    user_summary_list = []

    for user in users:
        print(f"\nОбработка пользователя {user.username} (ID: {user.id})")
        
        user_orders = Order.objects.filter(created_by=user).exclude(order_items__isnull=True).select_related('table', 'created_by')
        print(f"Количество заказов пользователя: {user_orders.count()}")

        closed_orders = user_orders.filter(is_completed=True)
        total_closed_tables = closed_orders.count()
        print(f"Количество закрытых столов: {total_closed_tables}")

        # Чаевые за сегодня
        today_total_tips = TipDistribution.objects.filter(user=user, tip__order__created_at__date=today).aggregate(Sum('amount'))['amount__sum'] or 0
        print(f"Чаевые за сегодня: {today_total_tips}")

        # Чаевые за текущий месяц
        current_month_tips = TipDistribution.objects.filter(user=user, tip__order__created_at__date__gte=first_day_of_current_month).aggregate(Sum('amount'))['amount__sum'] or 0
        print(f"Чаевые за текущий месяц: {current_month_tips}")

        user_summary_list.append({
            'user': user,
            'current_month_tips': current_month_tips,
            'today_total_tips': today_total_tips,
        })

    context = {
        'user_summary_list': user_summary_list,
        'is_admin': request.user.is_superuser
    }
    return render(request, 'user_summary.html', context)

@login_required
def user_detail(request, user_id):
    user = get_object_or_404(User, id=user_id)
    
    closed_orders = Order.objects.filter(created_by=user, is_completed=True).select_related('table', 'created_by')
    total_closed_tables = closed_orders.count()
    total_order_amount, total_tips_all_time, tip_ratio_all_time = calculate_totals(user, closed_orders)

    today = timezone.localtime(timezone.now())
    year = today.year
    month = today.month

    first_day_of_month = today.replace(day=1)
    last_day = calendar.monthrange(year, month)[1]
    last_day_of_month = today.replace(day=last_day)

    date_ranges = {
        'Сегодня': (today.replace(hour=0, minute=0, second=0, microsecond=0), today),
        'Месяц': (first_day_of_month, today)
    }
    
    stats = {}
    for period_name, (start_date, end_date) in date_ranges.items():
        period_orders = closed_orders.filter(created_at__gte=start_date, created_at__lte=end_date)
        total_order_amount_period, period_total_tips, period_tip_ratio = calculate_totals(user, period_orders)

        # Обновление для сбора чаевых, полученных пользователем за период
        period_total_tips = TipDistribution.objects.filter(
            user=user, tip__date__gte=start_date, tip__date__lte=end_date
        ).aggregate(Sum('amount'))['amount__sum'] or 0
        
        stats[period_name] = {
            'order_count': period_orders.count(),
            'total_order_amount': total_order_amount_period,
            'total_tips': period_total_tips,
            'tip_ratio': period_tip_ratio,
        }

        print(f"\nПериод: {period_name}")
        print(f"Сумма заказов: {total_order_amount_period}")
        print(f"Чаевые: {period_total_tips}")
        print(f"Соотношение: {period_tip_ratio}%")
        print(f"Количество заказов за период: {period_orders.count()}")

    today_orders = closed_orders.filter(created_at__date=today.date())
    today_total_order_amount, today_total_tips, today_tip_ratio = calculate_totals(user, today_orders)

    # Обновление для чаевых за сегодня
    today_total_tips = TipDistribution.objects.filter(
        user=user, tip__date__date=today.date()
    ).aggregate(Sum('amount'))['amount__sum'] or 0

    print(f"Сумма заказов за сегодня: {today_total_order_amount}")
    print(f"Чаевые за сегодня: {today_total_tips}")
    print(f"Соотношение чаевых к заказам за сегодня: {today_tip_ratio}%")

    tip_dates = TipDistribution.objects.filter(user=user).dates('tip__date', 'day')
    order_dates = closed_orders.dates('created_at', 'day')
    event_dates = set(tip_dates) | set(order_dates)

    events = {
        date.strftime('%Y-%m-%d'): {
            'total_order_amount': OrderItem.objects.filter(order__created_at__date=date).aggregate(total=Sum(F('quantity') * F('product__product_price')))['total'] or 0,
            'total_tips': TipDistribution.objects.filter(user=user, tip__date__date=date).aggregate(Sum('amount'))['amount__sum'] or 0,
        } for date in event_dates
    }

    today_str = today.strftime('%Y-%m-%d')
    if today_str in events:
        print("\nИнформация из календаря за сегодня:")
        print(f"Дата: {today_str}")
        print(f"Сумма заказов: {events[today_str]['total_order_amount']}")
        print(f"Чаевые: {events[today_str]['total_tips']}")

    tips_with_sharing = []
    tip_distributions = TipDistribution.objects.filter(user=user).select_related('tip').order_by('-tip__date')

    for tip in tip_distributions:
        shared_with = TipDistribution.objects.filter(tip=tip.tip).exclude(user=tip.user).select_related('user')
        shared_with_info = [{'user': share.user, 'amount': share.amount} for share in shared_with] if shared_with else '-'
        tips_with_sharing.append({
            'user': tip.user,
            'amount': tip.amount,
            'date': tip.tip.date,
            'shared_with': shared_with_info
        })

    return render(request, 'user_detail.html', {
        'user': user,
        'total_closed_tables': total_closed_tables,
        'total_order_amount': total_order_amount,
        'total_tips_all_time': total_tips_all_time,
        'tip_ratio_all_time': tip_ratio_all_time,
        'today_total_order_amount': today_total_order_amount,
        'today_total_tips': today_total_tips,
        'today_tip_ratio': today_tip_ratio,
        'total_closed_tables_today': today_orders.count(),
        'stats': stats,
        'events': json.dumps(events, cls=DecimalEncoder),
        'tips_with_sharing': tips_with_sharing,
    })


