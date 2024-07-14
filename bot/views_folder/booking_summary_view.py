from datetime import datetime, date
from django.utils import timezone
from django.db.models import Q
from rest_framework.decorators import api_view
from rest_framework.response import Response
from restaurant_app.models.tables import Booking
from ..serializers import BookingSerializer

@api_view(['GET'])
def api_booking_summary(request):
    selected_date_str = request.GET.get('date')
    selected_date = datetime.strptime(selected_date_str, '%Y-%m-%d').date() if selected_date_str else date.today()

    bookings = Booking.objects.filter(
        Q(reserved_date=selected_date) & Q(is_deleted=False)
    ).select_related('user', 'table')

    serializer = BookingSerializer(bookings, many=True)
    return Response(serializer.data)
