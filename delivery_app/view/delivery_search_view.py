from django.shortcuts import render
from django.db.models import Q
from delivery_app.forms import ProductQuantityForm
from restaurant_app.models.product import Product

def delivery_search_view(request, delivery_phone_number):
    query = request.GET.get('q')
    product_item = Product.objects.filter(Q(product_name_rus__icontains=query))
    category = request.GET.get('category', 'category')
    print(delivery_phone_number)
    product_quantity_form = ProductQuantityForm()
    context = {
        'query': query,
        'products': product_item,
        'product_quantity_form': product_quantity_form,
        'delivery_phone_number': delivery_phone_number,
        'category': category
    }
    return render(request, 'delivery_results.html', context)
