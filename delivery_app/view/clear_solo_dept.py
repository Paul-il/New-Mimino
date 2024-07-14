from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from delivery_app.models import Courier


@csrf_exempt
def clear_solo_debt(request):
    if request.method == "POST":
        # здесь вы можете обновить запись в базе данных
        # например, установите поле is_cleared=True для определенной записи
        # courier = Courier.objects.get(name="Соло")
        # courier.is_cleared = True
        # courier.save()
        
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'})
