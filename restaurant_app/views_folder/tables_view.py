from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Sum, F

from ..forms import OrderForm
from ..models.orders import Order
from ..models.tables import Table, Room

@login_required
def tables_view(request, room_id):  # добавьте room_id как параметр
    room = get_object_or_404(Room, id=room_id)  # получите комнату по id
    tables = room.tables.all()  # получите все столы для этой комнаты

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
        'tables': tables,
        'room': room  # добавьте комнату в контекст
    }
    return render(request, 'rooms.html', context)

@login_required
def table_order_view(request, table_id):
    table = get_object_or_404(Table, table_id=table_id)
    active_order = table.get_active_order()
    if active_order is None:
        order = Order(table=table, created_by=request.user, table_number=table.table_id)
        order.save()
    else:
        order = active_order

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            product_id = form.cleaned_data['product']
            quantity = form.cleaned_data['quantity']
            order.add_to_cart(product_id, quantity)
            order.save()
            return redirect('menu', table_id=table_id)
    else:
        form = OrderForm()

    if active_order is not None:
        active_order_items = active_order.order_items.annotate(total_price=F('quantity') * F('product__product_price'))
        active_order_total = active_order_items.aggregate(Sum('total_price')).get('total_price__sum') or 0
    else:
        active_order_items = None
        active_order_total = 0

    return render(request, 'table_order.html', {
        'table': table,
        'form': form,
        'active_order': order,
        'active_order_items': active_order_items,
        'active_order_total': active_order_total,
    })
