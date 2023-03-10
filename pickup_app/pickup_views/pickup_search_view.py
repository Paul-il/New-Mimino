from django.shortcuts import render
from django.db.models import Q
from pickup_app.forms import ProductQuantityForm
from restaurant_app.models.product import Product

def pickup_search_products_view(request, phone_number):
    query = request.GET.get('q', '')
    product_items = Product.objects.filter(Q(product_name_rus__icontains=query))
    product_quantity_form = ProductQuantityForm()
    context = {
        'query': query,
        'products': product_items,
        'product_quantity_form': product_quantity_form,
        'phone_number': phone_number
    }
    return render(request, 'pickup_search_results.html', context)
