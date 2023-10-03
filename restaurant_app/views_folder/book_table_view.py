from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.urls import reverse

from ..models.orders import Order,OrderItem
from ..models.tables import Table, Booking
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

            # Создание заказа
            order = Order.objects.create(
                table=booking.table,
                created_by=request.user,
                is_completed=False,
            )
        
            # Добавление продуктов из категории "банкет" в заказ
            banket_products = booking.get_banket_products()

            for product in banket_products:
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=1
                )
            
            messages.success(request, 'Стол успешно забронирован.')
            return redirect('bookings')
    else:
        form = BookingForm(request=request)

    messages.success(request, 'Стол успешно забронирован.')
    return render(request, 'restaurant_app/bookings.html', {'form': form, 'table': table})

def guests_not_arrived_view(request, booking_id):
    if request.method == "POST":
        # Получаем объект бронирования по переданному ID
        booking = get_object_or_404(Booking, id=booking_id)

        # Отмечаем, что гости не пришли
        booking.guests_did_not_arrive = True
        
        # Отмечаем бронирование как "удаленное" (но фактически не удаляем из базы данных)
        booking.is_deleted = True

        booking.save()

        # Сообщаем пользователю, что бронирование было обновлено
        messages.success(request, 'Бронирование обновлено.')

        return redirect('bookings')  # предполагается, что у вас есть URL с именем 'bookings'
