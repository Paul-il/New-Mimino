from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse

from ..models.orders import Order

@login_required
def close_table_view(request):
    if request.method == 'POST':
        table_id = request.POST.get('table_id')
        order = get_object_or_404(Order, table_id=table_id, is_completed=False)

        # Проверка наличия элементов в заказе
        if not order.order_items.exists():
            order.delete()
        else:
            order.is_completed = True
            order.save()

        table = order.table
        table.is_available = True
        table.save()
        return redirect('rooms')
    else:
        return HttpResponse("Not Supported Method")