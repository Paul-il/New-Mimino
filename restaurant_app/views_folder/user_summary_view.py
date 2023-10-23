from django.shortcuts import render, get_object_or_404
from django.contrib.auth.models import User
from ..models.tables import TipDistribution
from ..models.orders import Order, OrderItem
from django.db.models import Sum, F
from datetime import timedelta
from django.utils import timezone
import random
import json
from django.contrib.auth.decorators import login_required
import decimal

class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, decimal.Decimal):
            return float(obj)
        return super(DecimalEncoder, self).default(obj)

@login_required
def user_summary(request):
    users = User.objects.all()
    user_summary_list = []
    
    today = timezone.now().date()

    for user in users:
        user_orders = Order.objects.filter(created_by=user).exclude(order_items__isnull=True)
        
        # Get total order amount for the user
        total_order_amount = OrderItem.objects.filter(order__in=user_orders).aggregate(total=Sum(F('quantity') * F('product__product_price')))['total'] or 0
        
        closed_orders = user_orders.filter(is_completed=True)
        total_closed_tables = closed_orders.count()
        total_tips_all_time = TipDistribution.objects.filter(user=user).aggregate(Sum('amount'))['amount__sum'] or 0

        tip_ratio_all_time = round((total_tips_all_time / total_order_amount) * 100, 1) if total_order_amount > 0 else 0

        today_total_order_amount = OrderItem.objects.filter(order__in=closed_orders, order__created_at__date=today).aggregate(total=Sum(F('quantity') * F('product__product_price')))['total'] or 0
        today_total_tips = TipDistribution.objects.filter(user=user, tip__date__date=today).aggregate(Sum('amount'))['amount__sum'] or 0
        today_tip_ratio = round((today_total_tips / today_total_order_amount) * 100, 1) if today_total_order_amount > 0 else 0

        goal_increment = random.choice(range(15, 51, 5))
        total_goal = total_tips_all_time + goal_increment

        user_summary_list.append({
            'user': user,
            'total_closed_tables': total_closed_tables,
            'total_order_amount': total_order_amount,
            'total_tips_all_time': total_tips_all_time,
            'tip_ratio': tip_ratio_all_time,
            'today_total_order_amount': today_total_order_amount,
            'today_total_tips': today_total_tips,
            'today_tip_ratio': today_tip_ratio,
            'goal': total_goal,
        })

    context = {
        'user_summary_list': user_summary_list,
    }

    return render(request, 'user_summary.html', context)


@login_required
def user_detail(request, user_id):
    user = get_object_or_404(User, id=user_id)
    
    # Get total order amount for the user
    total_order_amount = OrderItem.objects.filter(order__created_by=user).aggregate(total=Sum(F('quantity') * F('product__product_price')))['total'] or 0

    closed_orders = Order.objects.filter(created_by=user, is_completed=True)
    total_closed_tables = closed_orders.count()
    total_tips_all_time = TipDistribution.objects.filter(user=user).aggregate(Sum('amount'))['amount__sum'] or 0
    tip_ratio_all_time = round((total_tips_all_time / total_order_amount) * 100, 1) if total_order_amount > 0 else 0

    today = timezone.localtime(timezone.now())
    
    first_day_of_month = today.replace(day=1)
    if today.month == 12:  # If current month is December
        last_day_of_month = today.replace(year=today.year + 1, month=1, day=1) - timedelta(days=1)
    else:
        last_day_of_month = today.replace(month=today.month + 1, day=1) - timedelta(days=1)

    date_ranges = {
        'Сегодня': (today.date(), today.date()),
        '7_Дней': (today - timedelta(days=7), today.date()),
        '14_Дней': (today - timedelta(days=14), today.date()),
        '21_Дней': (today - timedelta(days=21), today.date()),
        'Месяц': (first_day_of_month.date(), last_day_of_month.date())
    }


    stats = {}

    for period_name, (start_date, end_date) in date_ranges.items():
        period_orders = closed_orders.filter(created_at__date__gte=start_date, created_at__date__lte=end_date)
        period_order_count = period_orders.count()
        period_total_order_amount = OrderItem.objects.filter(order__in=period_orders).aggregate(total=Sum(F('quantity') * F('product__product_price')))['total'] or 0
        period_total_tips = TipDistribution.objects.filter(user=user, tip__date__date__gte=start_date, tip__date__date__lte=end_date).aggregate(Sum('amount'))['amount__sum'] or 0
        period_tip_ratio = round((period_total_tips / period_total_order_amount) * 100, 1) if period_total_order_amount > 0 else 0

        stats[period_name] = {
            'order_count': period_order_count,
            'total_order_amount': period_total_order_amount,
            'total_tips': period_total_tips,
            'tip_ratio': period_tip_ratio,
        }

    tip_dates = TipDistribution.objects.filter(user=user).dates('tip__date', 'day')
    order_dates = closed_orders.dates('created_at', 'day')
    event_dates = set(tip_dates) | set(order_dates)
    
    events = {
        date.strftime('%Y-%m-%d'): {
            'total_order_amount': OrderItem.objects.filter(order__created_at__date=date).aggregate(total=Sum(F('quantity') * F('product__product_price')))['total'] or 0,
            'total_tips': TipDistribution.objects.filter(user=user, tip__date__date=date).aggregate(Sum('amount'))['amount__sum'] or 0,
        } for date in event_dates
    }

    return render(request, 'user_detail.html', {
        'user': user,
        'total_closed_tables': total_closed_tables,
        'total_order_amount': total_order_amount,
        'total_tips_all_time': total_tips_all_time,
        'tip_ratio_all_time': tip_ratio_all_time,
        'stats': stats,
        'events': json.dumps(events, cls=DecimalEncoder),
    })
