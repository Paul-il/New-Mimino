from django.shortcuts import render
from django.utils import timezone
from ..models.orders import OrderItem, Order
# Убедитесь, что импортируете модель Product, если она находится в другом месте
from ..models.product import Product, OrderChangeLog

def find_products(request):
    query = request.GET.get('query', '').strip()
    today = timezone.now().date()  # Получаем текущую дату
    products = []

    if query:
        products = OrderItem.objects.filter(
            product__product_name_rus__icontains=query, 
            is_delivered=False,
            order__orderchangelog__change_time__date=today  # Фильтр по текущей дате
        ).distinct().select_related('order', 'product', 'order__created_by')  # Добавляем выборку created_by

        for product in products:
            product_logs = OrderChangeLog.objects.filter(
                order=product.order, 
                product_name=product.product.product_name_rus, 
                change_time__date=today
            ).order_by('-change_time')
            if product_logs.exists():
                product.change_time = product_logs.first().change_time
            else:
                product.change_time = None

    return render(request, 'find_product.html', {'products': products})
