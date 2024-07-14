import csv
import os
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.models import User
from ..models.tables import TipDistribution
from ..models.orders import Order, OrderItem
from django.db.models import Sum, F, Prefetch
from django.utils import timezone
from django.utils.timezone import localtime
from django.contrib.auth.decorators import login_required
import json
import decimal
import calendar
from django.conf import settings

class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, decimal.Decimal):
            return float(obj)
        return super(DecimalEncoder, self).default(obj)

def update_tips_csv(start_date=None, end_date=None):
    csv_file_path = os.path.join(settings.BASE_DIR, 'tips.csv')

    # Получить чаевые из базы данных за указанные даты
    tips = TipDistribution.objects.select_related('user', 'tip')
    if start_date and end_date:
        tips = tips.filter(tip__date__range=[start_date, end_date])

    with open(csv_file_path, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['user_id', 'username', 'tip_amount', 'tip_date'])

        for tip in tips:
            writer.writerow([tip.user.id, tip.user.username, tip.amount, tip.tip.date])

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

    users = User.objects.prefetch_related(
        'bookings',
        'userprofile',
        'tipgoal',
        Prefetch('order_set', queryset=Order.objects.select_related('table', 'created_by').exclude(order_items__isnull=True))
    ).all()

    user_summary_list = []

    for user in users:
        user_orders = user.order_set.all()
        closed_orders = user_orders.filter(is_completed=True)
        total_closed_tables = closed_orders.count()

        # Чаевые за сегодня
        today_total_tips = TipDistribution.objects.filter(
            user=user, 
            tip__date__date=today
        ).aggregate(Sum('amount'))['amount__sum'] or 0

        # Чаевые за текущий месяц
        current_month_tips = TipDistribution.objects.filter(
            user=user, 
            tip__date__date__gte=first_day_of_current_month
        ).aggregate(Sum('amount'))['amount__sum'] or 0

        user_summary_list.append({
            'user': user,
            'current_month_tips': current_month_tips,
            'today_total_tips': today_total_tips,
        })

        # Отладочная информация
        print(f"Пользователь: {user.username}, Чаевые за сегодня: {today_total_tips}, Чаевые за месяц: {current_month_tips}")

    # Сортировка по чаевым за сегодня в порядке убывания
    user_summary_list.sort(key=lambda x: x['today_total_tips'], reverse=True)

    context = {
        'user_summary_list': user_summary_list,
        'is_admin': request.user.is_superuser
    }
    return render(request, 'user_summary.html', context)



@login_required
def user_detail(request, user_id):
    user = get_object_or_404(User.objects.prefetch_related(
        Prefetch('order_set', queryset=Order.objects.select_related('table', 'created_by').filter(is_completed=True))
    ), id=user_id)
    
    closed_orders = user.order_set.all()
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

    # Обновление CSV файла
    update_tips_csv(first_day_of_month, today)

    csv_file_path = os.path.join(settings.BASE_DIR, 'tips.csv')
    events = {}

    with open(csv_file_path, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            date_str = row['tip_date']
            if date_str not in events:
                events[date_str] = {
                    'total_order_amount': 0,
                    'total_tips': 0,
                }
            events[date_str]['total_tips'] += float(row['tip_amount'])

    tips_with_sharing = []
    tip_distributions = TipDistribution.objects.filter(user=user).select_related('tip').order_by('-tip__date')

    for tip in tip_distributions:
        order = tip.tip.order  # Используйте временную переменную для order
        table_id = order.table.table_id if order and order.table else '-'
        order_id = order.id if order else ''
        order_amount = order.get_total_amount() if order else 0
        num_people = order.num_of_people if order else 0

        shared_with = TipDistribution.objects.filter(tip=tip.tip).exclude(user=tip.user).select_related('user')
        shared_with_info = [{'user': share.user, 'amount': share.amount} for share in shared_with] if shared_with else '-'
        tips_with_sharing.append({
            'user': tip.user,
            'amount': tip.amount,
            'date': tip.tip.date,
            'shared_with': shared_with_info,
            'table_id': table_id,
            'order_id': order_id,
            'order_amount': order_amount,
            'num_people': num_people
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
        'is_admin': request.user.is_superuser,  # Ensure this line is present
    })

