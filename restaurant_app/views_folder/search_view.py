from ..models.product import Product
from django.shortcuts import render
from ..forms import ProductQuantityForm

def search_products_view(request):
    query = request.GET.get('q', '')
    if query:
        products = Product.objects.filter(product_name_rus__icontains=query)
    else:
        products = Product.objects.none()
    product_quantity_form = ProductQuantityForm()

    context = {'query': query, 
               'products': products,
               'product_quantity_form': product_quantity_form,}

    return render(request,'search_results.html', context=context)

