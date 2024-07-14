from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from delivery_app.models import DeliveryCustomer, DeliveryOrder
from django.utils import timezone

@login_required
def future_orders_view(request):
    """
    Отображает будущие заказы.

    Args:
        request: HttpRequest объект.

    Returns:
        HttpResponse объект с отображением будущих заказов.
    """
    future_orders = DeliveryOrder.objects.filter(
        delivery_date__gt=timezone.now().date(),
        is_completed=False
    )

    return render(request, 'future_orders_template.html', {
        'future_orders': future_orders
    })

