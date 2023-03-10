from django.shortcuts import render, redirect
from django.urls import reverse

from django.contrib.auth.decorators import login_required

from .models.tables import Table, Booking
from .models.orders import Order, OrderItem
from .models.product import Product

from .forms import GuestsHereForm, BookingForm
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.utils import timezone




########################################################################################

@login_required
def book_table_view(request, table_id):
    table = get_object_or_404(Table, table_id=table_id)
    if request.method == 'POST':
        form = BookingForm(request.POST, request=request)
        if form.is_valid():
            form.save()
            return redirect('tables')
    else:
        form = BookingForm(request=request)
    return render(request, 'book_table.html', {'table': table, 'form': form})



@login_required
def bookings_view(request):
    bookings = Booking.objects.all()
    context = {'bookings': bookings}
    return render(request, 'bookings.html', context)

@login_required
def guests_here_view(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    if request.method == 'POST':
        form = GuestsHereForm(request.POST, instance=booking)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.are_guests_here = not booking.are_guests_here
            booking.user = request.user
            if booking.are_guests_here:
                booking.table.is_booked = False
                booking.table.are_guests_here = True
                booking.table.save()
                booking.is_deleted = True
            booking.save()
            messages.success(request, 'Статус гостей обновлен.')
            return redirect('bookings')
    else:
        form = GuestsHereForm(instance=booking, initial={'are_guests_here': booking.are_guests_here})
    return render(request, 'guests_here.html', {'form': form, 'booking': booking})


def start_order_view(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    order.order_time = timezone.now()  # Update order_time field to current time
    order.save()
    return redirect('order_detail', order_id=order_id)










############################ ADD_DELETE ##################################



