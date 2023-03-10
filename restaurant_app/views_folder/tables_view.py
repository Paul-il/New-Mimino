from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

from ..forms import OrderForm
from ..models.orders import Order
from ..models.tables import Table

@login_required
def tables_view(request):
    tables = Table.objects.all()

    for table in tables:
        if table.orders.filter(is_completed=False).exists():
            table.active_order = True
        else:
            table.active_order = False

    context = {'tables': tables}
    return render(request, 'tables.html', context)

@login_required
def table_order_view(request, table_id):
    table = get_object_or_404(Table, table_id=table_id)
    active_order = table.get_active_order()

    if active_order is None:
        order = Order(table=table)
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
        active_order_items = active_order.order_items.all()
        active_order_total = active_order.get_total_price()
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
