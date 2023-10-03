from .models.tables import Booking

def booking_exists(request):
    has_bookings = Booking.objects.filter(is_deleted=False).exists()
    return {'has_bookings': has_bookings}
