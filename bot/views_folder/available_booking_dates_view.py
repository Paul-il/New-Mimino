from datetime import datetime, timedelta
from django.utils import timezone
from rest_framework.decorators import api_view
from rest_framework.response import Response
from restaurant_app.models.tables import Booking

@api_view(['GET'])
def api_available_booking_dates(request):
    start_date = timezone.now().date()
    end_date = start_date + timedelta(days=7)  # Например, показываем даты на неделю вперёд
    bookings = Booking.objects.filter(reserved_date__range=(start_date, end_date)).values('reserved_date').distinct()
    available_dates = [booking['reserved_date'].strftime('%Y-%m-%d') for booking in bookings]

    return Response({'available_dates': available_dates})
