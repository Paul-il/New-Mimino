from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from ..models.orders import Order
from ..models.tables import Table

@login_required
def table_detail(request, table_id, order_id):
    table = get_object_or_404(Table, pk=table_id)
    order = get_object_or_404(Order, pk=order_id, table=table)

    order_details = {
        'id': order.id,
        'closed_at': order.updated_at,
        'num_of_people': order.num_of_people,
        'total_sum': order.total_sum(),
        'order_items': order.order_items.select_related('product').all()
    }

    context = {
        'table': table,
        'order': order_details
    }

    return render(request, 'table_detail.html', context)
