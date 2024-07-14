from django.shortcuts import render, redirect, get_object_or_404
from ..models.product import Product
from django.views.decorators.http import require_GET, require_POST
from django.contrib.auth.decorators import login_required

@login_required
@require_GET
def manage_products(request):
    products = Product.objects.all().order_by('product_name_rus')
    available_products = [product for product in products if product.is_available and product.show_in_menu]
    unavailable_products = [product for product in products if not product.is_available and product.show_in_menu]
    
    return render(request, 'manage_products.html', {'available_products': available_products, 'unavailable_products': unavailable_products})

@login_required
@require_POST
def toggle_product_availability(request):
    product = get_object_or_404(Product, id=request.POST.get('product_id'))
    product.is_available = not product.is_available
    product.save()
    
    return redirect('manage_products')
