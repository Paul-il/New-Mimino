from django.shortcuts import render, redirect
from ..models.product import Product
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required

@login_required
@require_http_methods(["GET", "POST"])
def manage_products(request):
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        toggle = request.POST.get('toggle')  # получаем значение из кнопки
        product = Product.objects.get(id=product_id)
        product.is_available = True if toggle == 'Enable' else False
        product.save()
        return redirect('manage_products')

    available_products = Product.objects.filter(is_available=True).order_by('product_name_rus')
    unavailable_products = Product.objects.filter(is_available=False)
    return render(request, 'manage_products.html', {'available_products': available_products, 'unavailable_products': unavailable_products})
