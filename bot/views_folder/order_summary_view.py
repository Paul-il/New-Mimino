# bot/views_folder/order_summary_view.py
from datetime import datetime, date
from rest_framework.decorators import api_view
from rest_framework.response import Response
from bot.views_folder.helpers import get_summary_data
from restaurant_app.models.orders import Order
from pickup_app.models import PickupOrder
from delivery_app.models import DeliveryOrder
from bot.serializers import OrderSummarySerializer
import logging

logger = logging.getLogger(__name__)

@api_view(['GET'])
def api_order_summary(request):
    try:
        selected_date_str = request.GET.get('date')
        selected_date = datetime.strptime(selected_date_str, '%Y-%m-%d').date() if selected_date_str else date.today()
        
        start_date = selected_date
        end_date = selected_date

        total_orders_today, total_orders_sum = get_summary_data(Order, start_date, end_date, "total_price")
        total_pickup_orders_today, total_pickup_orders_sum = get_summary_data(PickupOrder, start_date, end_date, "total_amount")
        total_delivery_orders_today, total_delivery_orders_sum = get_summary_data(DeliveryOrder, start_date, end_date, "total_amount")

        total_all_orders_sum = total_orders_sum + total_pickup_orders_sum + total_delivery_orders_sum
        total_all_orders_today = total_orders_today + total_pickup_orders_today + total_delivery_orders_today

        data = {
            'total_orders_today': total_orders_today,
            'total_orders_sum': total_orders_sum,
            'total_pickup_orders_today': total_pickup_orders_today,
            'total_pickup_orders_sum': total_pickup_orders_sum,
            'total_delivery_orders_today': total_delivery_orders_today,
            'total_delivery_orders_sum': total_delivery_orders_sum,
            'total_all_orders_sum': total_all_orders_sum,
            'total_all_orders_today': total_all_orders_today
        }

        serializer = OrderSummarySerializer(data)
        return Response(serializer.data)
    except Exception as e:
        logger.error(f"Error in api_order_summary: {str(e)}", exc_info=True)
        return Response({"error": str(e)}, status=500)
