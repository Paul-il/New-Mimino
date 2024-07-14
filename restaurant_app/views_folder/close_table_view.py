from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.db import transaction

from ..models.orders import Order
from ..models.tables import Table, VirtualTable, Tip

@login_required
def close_table_view(request):
    if request.method == 'POST':
        table_id = request.POST.get('table_id')
        order = get_object_or_404(Order, table__id=table_id, is_completed=False)

        # Проверка наличия чаевых
        if not Tip.objects.filter(order=order).exists():
            return HttpResponse("Tips are required before closing the table.", status=400)

        with transaction.atomic():
            # Проверка наличия элементов в заказе
            if not order.order_items.exists():
                order.delete()
            else:
                order.is_completed = True
                order.save()

            table = order.table
            table.is_available = True
            table.save()

            # Закрытие виртуальных столов
            virtual_tables = table.virtual_tables.all()
            for virtual_table in virtual_tables:
                virtual_table.is_closed = True
                virtual_table.save()

                virtual_orders = Order.objects.filter(table=table, table_number=f"Virtual-{virtual_table.id}")
                for virtual_order in virtual_orders:
                    virtual_order.is_completed = True
                    virtual_order.save()

        return redirect('rooms')
    else:
        return HttpResponse("Not Supported Method", status=405)
