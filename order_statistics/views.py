from django.http import JsonResponse
from .models import get_daily_orders

def daily_orders(request):
    data = get_daily_orders()
    return JsonResponse(list(data), safe=False)
