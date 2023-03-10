from ..models.product import Product
from django.shortcuts import render

def search_products_view(request):
    
    query = request.GET.get('q', '')
    if query:
        products = Product.objects.filter(product_name_rus__icontains=query)
    else:
        products = Product.objects.none()
    context = {'query': query, 'products': products}

    return render(request,'search_results.html', context=context)
