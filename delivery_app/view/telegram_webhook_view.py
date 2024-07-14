from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json

@csrf_exempt  # Отключение проверки CSRF для этого представления
@require_http_methods(["POST"])  # Принимать только POST-запросы
def telegram_webhook(request):
    data = json.loads(request.body.decode('utf-8'))
    # Обработка данных от Telegram
    # ...
    return JsonResponse({"status": "ok"})
