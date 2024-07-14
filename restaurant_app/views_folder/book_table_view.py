from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.core.exceptions import ValidationError
from ..models.orders import Order, OrderItem
from ..models.tables import Booking
from ..forms import BookingForm

import logging
# Configure logger
logger = logging.getLogger(__name__)

@login_required
def edit_booking_view(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)

    if request.method == 'POST':
        form = BookingForm(request.POST, instance=booking)
        if form.is_valid():
            form.save()
            messages.success(request, 'Бронирование успешно обновлено.')
            return redirect('bookings')
        else:
            messages.error(request, 'Исправьте ошибки в форме.')
    else:
        form = BookingForm(instance=booking)

    return render(request, 'edit_booking.html', {'form': form, 'booking_id': booking_id})


@login_required
def book_table_view(request):
    if request.method == 'POST':
        form = BookingForm(request.POST, request=request)
        if form.is_valid():
            try:
                with transaction.atomic():
                    booking = create_booking_and_order(request, form)
                messages.success(request, 'Стол успешно забронирован.')
                return redirect('bookings')
            except Exception as e:
                messages.error(request, f'Ошибка при бронировании стола: {e}')
                logger.error(f'Error booking table: {e}', exc_info=True)
        else:
            messages.error(request, 'Исправьте ошибки в форме.')
    else:
        form = BookingForm(request=request)

    return render(request, 'restaurant_app/book_table.html', {'form': form})


@login_required
def create_booking_and_order(request, form):
    try:
        booking = form.save(commit=False)
        booking.user = request.user
        booking.table = form.cleaned_data['table']  # Получение выбранного стола из очищенных данных
        booking.save()

        order = Order.objects.create(
            table=booking.table,
            created_by=request.user,
            is_completed=False,
        )

        banket_products = booking.get_banket_products()
        order_items = [
            OrderItem(order=order, product=product, quantity=1)
            for product in banket_products
        ]
        OrderItem.objects.bulk_create(order_items)
        
        return booking
    except ValidationError as e:
        raise e
    except Exception as e:
        logger.error(f'Error in creating booking and order: {e}', exc_info=True)
        raise e


@login_required
def guests_not_arrived_view(request, booking_id):
    if request.method == "POST":
        booking = get_object_or_404(Booking, id=booking_id)

        comment = request.POST.get('comment', '').strip()
        if comment:
            booking.description = comment

        booking.guests_did_not_arrive = True
        booking.is_deleted = True

        booking.save()

        messages.success(request, 'Бронирование обновлено.')
        return redirect('bookings')

    return render(request, 'error.html', {'message': 'Invalid request method.'})
