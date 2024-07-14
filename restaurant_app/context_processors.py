from django.db.models import Sum
from django.utils import timezone
from .models.tables import TipDistribution
from .models.message import Message

from datetime import datetime

def tips_and_goal(request):
    if request.user.is_authenticated:
        today = timezone.localtime(timezone.now()).date()
        start_datetime = timezone.make_aware(datetime.combine(today, datetime.min.time()))  # начало дня
        end_datetime = timezone.make_aware(datetime.combine(today, datetime.max.time()))  # конец дня
        today_total_tips = TipDistribution.objects.filter(user=request.user, tip__date__range=(start_datetime, end_datetime)).aggregate(total=Sum('amount'))['total'] or 0
        return {'tip_amount': today_total_tips}
    return {}


def unread_messages_count(request):
    if request.user.is_authenticated:
        return {'unread_messages_count': Message.objects.filter(read=False, chat__participants=request.user).count()}
    return {'unread_messages_count': 0}