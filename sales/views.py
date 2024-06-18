from django.shortcuts import render
from django.db.models import Sum
from restaurant_app.models.orders import OrderItem 

def statistics_view(request):
    # Получить все проданные товары
    sold_products = (OrderItem.objects
                     .values('product__product_name_rus', 'product__category')
                     .annotate(sold_count=Sum('quantity')))
    # Сгруппировать по категориям
    categories_data = {}
    for item in sold_products:
        category = item['product__category']
        product = item['product__product_name_rus']
        count = item['sold_count']
        if category in categories_data:
            categories_data[category]['total_count'] += count
            categories_data[category]['products'].append({product: count})
        else:
            categories_data[category] = {'total_count': count, 'products': [{product: count}]}

    context = {'categories_data': categories_data}
    return render(request, 'sales/statistics.html', context)
