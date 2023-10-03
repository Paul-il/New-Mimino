from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.db.models import Sum, F
from collections import defaultdict

from ..models.tables import Room

@login_required
def rooms_view(request):
    rooms = Room.objects.all().prefetch_related('tables')
    for room in rooms:
        tables_in_room = room.tables.all()
        waiters = defaultdict(list)
        for table in tables_in_room:
            active_order = table.get_active_order()
            if active_order:
                waiter_name = active_order.created_by.first_name
                waiters[waiter_name].append((table.id, active_order.id))
        room.waiters = dict(waiters)

    context = {'rooms': rooms}
    return render(request, 'rooms.html', context)

@login_required
def room_detail_view(request, room_id):
    room = get_object_or_404(Room, id=room_id)
    tables = room.tables.all()

    # Этот блок кода добавляет информацию о заказах к каждому столу
    for table in tables:
        active_order = table.get_active_order()
        if active_order:
            table.active_order = True
            active_order_items = active_order.order_items.annotate(total_price=F('quantity') * F('product__product_price'))
            active_order_total = active_order_items.aggregate(Sum('total_price')).get('total_price__sum') or 0
            created_by_name = active_order.created_by.first_name  # получаем имя пользователя, создавшего заказ
        else:
            table.active_order = False
            active_order_items = None
            active_order_total = 0
            created_by_name = None  # если заказ не существует, то и пользователя не может быть

        table.active_order_items = active_order_items
        table.active_order_total = active_order_total
        table.created_by_name = created_by_name  # добавляем имя пользователя в объект стола

    context = {
        'tables': tables,  # Это теперь список столов с добавленной информацией о заказах
        'room_name': room.name
    }
    return render(request, 'room_detail.html', context)

