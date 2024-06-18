from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Sum, F

from ..forms import OrderForm
from ..models.orders import Order
from ..models.tables import Table, Room

@login_required
def tables_view(request, room_id):
    room = get_object_or_404(Room, id=room_id)
    tables = room.tables.all().prefetch_related('orders')  # оптимизация запросов

    for table in tables:
        active_order = table.get_active_order()
        if active_order:
            table.active_order = True
            table.active_order_items, table.active_order_total, table.created_by_name = get_order_details(active_order)
        else:
            table.active_order = False
            table.active_order_items = None
            table.active_order_total = 0
            table.created_by_name = None

    context = {
        'tables': tables,
        'room': room
    }
    return render(request, 'rooms.html', context)

@login_required
def table_order_view(request, table_id):
    table = get_object_or_404(Table, table_id=table_id)
    active_order = table.get_active_order()

    if active_order is None:
        active_order = Order.objects.create(table=table, created_by=request.user, table_number=table.table_id)

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            product_id = form.cleaned_data['product']
            quantity = form.cleaned_data['quantity']
            active_order.add_to_cart(product_id, quantity)
            return redirect('menu', table_id=table_id)
    else:
        form = OrderForm()

    # Добавляем проверку на пустой заказ при выходе
    if request.method == 'GET' and not active_order.order_items.exists():
        active_order.delete()
        return redirect('rooms')

    active_order_items, active_order_total, _ = get_order_details(active_order) if active_order else (None, 0, None)

    return render(request, 'table_order.html', {
        'table': table,
        'form': form,
        'active_order': active_order,
        'active_order_items': active_order_items,
        'active_order_total': active_order_total,
    })

def get_order_details(order):
    """Helper function to get order details."""
    active_order_items = order.order_items.annotate(total_price=F('quantity') * F('product__product_price'))
    active_order_total = active_order_items.aggregate(Sum('total_price')).get('total_price__sum') or 0
    created_by_name = order.created_by.first_name
    return active_order_items, active_order_total, created_by_name
