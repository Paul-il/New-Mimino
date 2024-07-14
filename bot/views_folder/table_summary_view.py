# bot/views_folder/table_summary_view.py
from datetime import datetime, date
from django.utils import timezone
from django.db.models import Sum, F
from rest_framework.decorators import api_view
from rest_framework.response import Response
from restaurant_app.models.tables import Room
from collections import defaultdict

@api_view(['GET'])
def api_table_summary(request):
    rooms = Room.objects.all().prefetch_related('tables')
    table_summary = []

    for room in rooms:
        tables_in_room = room.tables.all()

        for table in tables_in_room:
            active_order = table.get_active_order()
            if active_order:
                waiter_name = active_order.created_by.first_name
                all_delivered = all(item.is_delivered for item in active_order.order_items.all())
                table_and_order_info = (table.id, active_order.id, all_delivered)  # Добавляем статус доставки

                active_order_items = active_order.order_items.all().annotate(total_price=F('quantity') * F('product__product_price'))
                active_order_total = active_order_items.aggregate(Sum('total_price')).get('total_price__sum') or 0

                table_summary.append({
                    'table_id': table.table_id,
                    'order_id': active_order.id,
                    'created_at': active_order.created_at,
                    'num_of_people': active_order.num_of_people,
                    'waiter_name': waiter_name,
                    'active_order_total': active_order_total,
                    'has_products': active_order_items.exists()
                })

    return Response(table_summary)
