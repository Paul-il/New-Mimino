# bot/views_folder/tip_summary_view.py
from datetime import datetime, date
from django.utils import timezone
from django.db.models import Sum
from rest_framework.decorators import api_view
from rest_framework.response import Response
from restaurant_app.models.tables import Tip, TipDistribution
from django.contrib.auth.models import User
import logging

logger = logging.getLogger(__name__)

@api_view(['GET'])
def api_tip_summary(request):
    try:
        selected_date_str = request.GET.get('date')
        selected_date = datetime.strptime(selected_date_str, '%Y-%m-%d').date() if selected_date_str else date.today()
        
        start_date = selected_date
        end_date = selected_date

        tips = Tip.objects.filter(
            order__created_at__range=(timezone.make_aware(datetime.combine(start_date, datetime.min.time())),
                                      timezone.make_aware(datetime.combine(end_date, datetime.max.time()))),
            amount__gt=0  # Фильтруем только чаевые с положительной суммой
        ).select_related('order', 'order__created_by')

        # Проверка наличия чаевых
        if not tips.exists():
            return Response([])

        user_tip_totals = TipDistribution.objects.filter(
            tip__in=tips
        ).values('user').annotate(total_amount=Sum('amount'))

        tip_summary = []
        for user_tip in user_tip_totals:
            user = User.objects.get(id=user_tip['user'])
            tip_summary.append({
                'user_id': user.id,
                'user_name': user.username,
                'first_name': user.first_name,
                'total_amount': user_tip['total_amount']
            })

        return Response(tip_summary)
    except Exception as e:
        logger.error(f"Error in api_tip_summary: {str(e)}", exc_info=True)
        return Response({"error": str(e)}, status=500)
