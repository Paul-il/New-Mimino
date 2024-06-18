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

@login_required
def book_table_view(request):
    if request.method == 'POST':
        form = BookingForm(request.POST, request=request)
        if form.is_valid():
            booking = form.save(commit=False)  # Создаем объект бронирования, но пока не сохраняем в базе данных
            booking.user = request.user

            # Теперь используем выбранный стол из очищенных данных формы
            selected_table = form.cleaned_data.get('table')
            if selected_table:
                booking.table = selected_table  # Устанавливаем выбранный стол
            else:
                # Обработка случая, если подходящий стол не был найден (можно добавить сообщение об ошибке)
                messages.error(request, 'Подходящий стол не найден.')
                return render(request, 'book_table.html', {'form': form})

            booking.save()  # Сохраняем объект бронирования в базе данных
            # ... остальная логика ...
            return redirect('ask_where')
    else:
        form = BookingForm(request=request)
    
    return render(request, 'book_table.html', {'form': form})



@login_required
def bookings_view(request):
    # Получаем текущую дату
    today = timezone.now().date()

    # Получаем и сортируем бронирования начиная с ближайшей даты к текущей
    bookings = Booking.objects.filter(reserved_date__gte=today, is_deleted=False).order_by('reserved_date', 'reserved_time')

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

@login_required
def start_order_view(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    order.order_time = timezone.now()  # Update order_time field to current time
    order.save()
    return redirect('order_detail', order_id=order_id)



