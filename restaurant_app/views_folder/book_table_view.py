from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.db import transaction
from django.core.exceptions import ValidationError
from ..models.orders import Order,OrderItem
from ..models.tables import Booking
from ..forms import BookingForm


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

    else:
        form = BookingForm(request=request)

    return render(request, 'restaurant_app/book_table.html', {'form': form})


@login_required
def create_booking_and_order(request, form):
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
    for product in banket_products:
        OrderItem.objects.create(
            order=order,
            product=product,
            quantity=1
        )
    return booking


@login_required
def guests_not_arrived_view(request, booking_id):
    if request.method == "POST":
        # Получаем объект бронирования по переданному ID
        booking = get_object_or_404(Booking, id=booking_id)

        # Получаем комментарий из запроса, если он был предоставлен
        comment = request.POST.get('comment', '').strip()
        if comment:
            booking.description = comment

        # Отмечаем, что гости не пришли
        booking.guests_did_not_arrive = True
        
        # Отмечаем бронирование как "удаленное" (но фактически не удаляем из базы данных)
        booking.is_deleted = True

        booking.save()

        # Сообщаем пользователю, что бронирование было обновлено
        messages.success(request, 'Бронирование обновлено.')

        return redirect('bookings')
