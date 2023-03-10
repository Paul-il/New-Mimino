from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from ..models.tables import Booking, Table
from ..forms import BookingForm


@login_required
def book_table_view(request, table_id):
    table = get_object_or_404(Table, table_id=table_id)

    if request.method == 'POST':
        form = BookingForm(request.POST, request=request)

        if form.is_valid():
            booking = form.save(commit=False)
            booking.user = request.user
            booking.save()
            messages.success(request, 'Стол успешно забронирован.')
            return redirect('bookings')
    else:
        form = BookingForm()
    messages.success(request, 'Стол успешно забронирован.')
    return render(request, 'restaurant_app/bookings.html', {'form': form, 'table': table})

def bookings(request):
    bookings = Booking.objects.filter(is_deleted=False).order_by('-created_at')

    context = {
        'bookings': bookings,
    }

    if request.method == 'POST':
        booking_id = request.POST.get('booking_id')
        booking = Booking.objects.get(pk=booking_id)
        booking.is_deleted = True
        booking.save()

        context['message'] = 'Бронь успешно удалена.'

    return render(request, 'bookings.html', context)

