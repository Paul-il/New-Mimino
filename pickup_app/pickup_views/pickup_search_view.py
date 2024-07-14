from django.shortcuts import render
from django.db.models import Q
from pickup_app.forms import ProductQuantityForm
from restaurant_app.models.product import Product

def pickup_search_products_view(request, phone_number):
    query = request.GET.get('q', '')
    products = Product.objects.filter(product_name_rus__icontains=query)
    product_quantity_form = ProductQuantityForm()
    category = request.GET.get('category', 'category')
    context = {
        'query': query,
        'products': products,
        'phone_number': phone_number,
        'product_quantity_form': product_quantity_form,
        'category': category,  # Pass category to the context with a default value.
    }
    return render(request, 'pickup_search_results.html', context)

