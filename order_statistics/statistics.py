from django.db.models import Count
from django.db import models
from .models import StatisticsOrder

def get_daily_orders():
    return StatisticsOrder.objects.annotate(date=models.functions.TruncDate('created_at')).values('date').annotate(order_count=Count('id')).order_by('date')
