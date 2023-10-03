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

    for user in users:
        user_orders = Order.objects.filter(created_by=user).exclude(order_items__isnull=True)
        total_price1 = 0

        for order in user_orders:
            for order_item in OrderItem.objects.filter(order=order):
                total_price1 += order_item.quantity * order_item.product.product_price

        closed_orders = user_orders.filter(is_completed=True)
        total_closed_tables = closed_orders.count()
        total_tips_all_time = TipDistribution.objects.filter(user=user).aggregate(Sum('amount'))['amount__sum'] or 0

        if total_price1 > 0:
            tip_ratio_all_time = round((total_tips_all_time / total_price1) * 100, 1)
        else:
            tip_ratio_all_time = 0

        today_total_order_amount = OrderItem.objects.filter(order__in=closed_orders, order__created_at__date=timezone.now().date()).aggregate(total=Sum(F('quantity') * F('product__product_price')))['total'] or 0
        today_total_tips = TipDistribution.objects.filter(user=user, tip__date__date=timezone.now().date()).aggregate(Sum('amount'))['amount__sum'] or 0

        if today_total_order_amount > 0:
            today_tip_ratio = round((today_total_tips / today_total_order_amount) * 100, 1)
        else:
            today_tip_ratio = 0

        goal_increment = random.choice(range(15, 51, 5))
        total_goal = total_tips_all_time + goal_increment

        user_summary_list.append({
            'user': user,
            'total_closed_tables': total_closed_tables,
            'total_order_amount': total_price1,
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
    user_orders = Order.objects.filter(created_by=user).exclude(order_items__isnull=True)
    total_price1 = 0

    for order in user_orders:
        for order_item in OrderItem.objects.filter(order=order):
            total_price1 += order_item.quantity * order_item.product.product_price

    closed_orders = user_orders.filter(is_completed=True)
    total_closed_tables = closed_orders.count()
    total_tips_all_time = TipDistribution.objects.filter(user=user).aggregate(Sum('amount'))['amount__sum'] or 0

    if total_price1 > 0:
        tip_ratio_all_time = round((total_tips_all_time / total_price1) * 100, 1)
    else:
        tip_ratio_all_time = 0

    today = timezone.localtime(timezone.now())
    seven_days_ago = timezone.localtime(timezone.now() - timedelta(days=7))
    fourteen_days_ago = timezone.localtime(timezone.now() - timedelta(days=14))
    twenty_one_days_ago = timezone.localtime(timezone.now() - timedelta(days=21))
    one_month_ago = timezone.localtime(timezone.now() - timedelta(days=30))

    periods = [
        ('Сегодня', today.date(), today.date()),
        ('7_Дней', seven_days_ago.date(), today.date()),
        ('14_Дней', fourteen_days_ago.date(), today.date()),
        ('21_Дней', twenty_one_days_ago.date(), today.date()),
        ('Месяц', one_month_ago.date(), today.date()),
    ]

    stats = {}

    for period_name, start_date, end_date in periods:
        period_orders = closed_orders.filter(created_at__date__gte=start_date, created_at__date__lte=end_date)
        period_order_count = period_orders.count()

        period_total_order_amount = OrderItem.objects.filter(order__in=period_orders).aggregate(total=Sum(F('quantity') * F('product__product_price')))['total'] or 0
        period_total_tips = TipDistribution.objects.filter(user=user, tip__date__date__gte=start_date, tip__date__date__lte=end_date).aggregate(Sum('amount'))['amount__sum'] or 0

        if period_total_order_amount > 0:
            period_tip_ratio = round((period_total_tips / period_total_order_amount) * 100, 1)
        else:
            period_tip_ratio = 0

        stats[period_name] = {
            'order_count': period_order_count,
            'total_order_amount': period_total_order_amount,
            'total_tips': period_total_tips,
            'tip_ratio': period_tip_ratio,
        }

    tip_dates = TipDistribution.objects.filter(user=user).dates('tip__date', 'day')
    order_dates = user_orders.filter(is_completed=True).dates('created_at', 'day')
    event_dates = list(set(tip_dates) | set(order_dates))
    event_dates = [date.strftime('%Y-%m-%d') for date in event_dates]

    events = {}
    for date in event_dates:
        date_orders = closed_orders.filter(created_at__date=date)
        date_total_order_amount = OrderItem.objects.filter(order__in=date_orders).aggregate(total=Sum(F('quantity') * F('product__product_price')))['total'] or 0
        date_total_tips = TipDistribution.objects.filter(user=user, tip__date__date=date).aggregate(Sum('amount'))['amount__sum'] or 0
        events[date] = {
            'total_order_amount': date_total_order_amount,
            'total_tips': date_total_tips,
        }

    return render(request, 'user_detail.html', {
        'user': user,
        'total_closed_tables': total_closed_tables,
        'total_order_amount': total_price1,
        'total_tips_all_time': total_tips_all_time,
        'tip_ratio_all_time': tip_ratio_all_time,
        'stats': stats,
        'events': json.dumps(events, cls=DecimalEncoder),
    })
