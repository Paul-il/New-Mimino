# bot/views_folder/utils.py
from datetime import datetime
from django.utils import timezone
from django.db.models import Sum

def get_summary_data(model, start_date, end_date, total_amount_attr):
    aware_start_date = timezone.make_aware(datetime.combine(start_date, datetime.min.time()))
    aware_end_date = timezone.make_aware(datetime.combine(end_date, datetime.max.time()))

    queryset = model.objects.filter(created_at__range=(aware_start_date, aware_end_date))

    count = queryset.count()
    total_sum = queryset.aggregate(total_sum=Sum(total_amount_attr))['total_sum'] or 0

    return count, total_sum
