from django.shortcuts import render, redirect
from restaurant_app.models.product import Product, ProductStock
from ..forms import ProductStockForm

def add_stock(request):
    if request.method == 'POST':
        form = ProductStockForm(request.POST)
        if form.is_valid():
            stock = form.save()
            # Обновление количества товара
            product = stock.product
            product.quantity += stock.received_quantity
            product.save()
            return redirect('add_stock')  # Перенаправление на ту же страницу для обновления информации
    else:
        form = ProductStockForm()

    # Получение всех поставок для отображения
    stocks = ProductStock.objects.all().order_by('-received_date')  # Предположим, у вас есть поле received_date

    return render(request, 'add_stock.html', {'form': form, 'stocks': stocks})
