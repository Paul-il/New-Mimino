from django.http import JsonResponse
from restaurant_app.models.product import Product

def search_products(request):
    query = request.GET.get('query', '')
    products = Product.objects.filter(name__icontains=query)[:5]  # Пример поиска по имени продукта
    results = [{'id': p.id, 'name': p.name} for p in products]
    return JsonResponse(results, safe=False)
