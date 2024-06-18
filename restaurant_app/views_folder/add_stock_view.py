import logging
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.db.models import Q
from ..models.product import Product, ProductStock
from ..forms import CategorySelectForm

# Configure logger
logger = logging.getLogger(__name__)

LOW_STOCK_THRESHOLD = 3

@login_required
def limited_products_view(request):
    categories = dict(Product.CATEGORY_CHOICES)
    selected_category = request.GET.get('category', '')

    products = Product.objects.filter(Q(category=selected_category) | Q(has_limit=True, limit_quantity__lt=10))
    low_stock_products = products.filter(limit_quantity__lte=LOW_STOCK_THRESHOLD)

    for product in low_stock_products:
        messages.warning(request, f'Внимание: количество продукта "{product.product_name_rus}" ниже порогового уровня.')

    form = CategorySelectForm(initial={'category': selected_category})

    return render(request, 'limited_products.html', {
        'form': form,
        'products': products,
        'categories': categories,
    })

@login_required
def update_product_stock(request, product_id):
    product = get_object_or_404(Product, id=product_id, has_limit=True)
    if request.method == 'POST':
        try:
            received_quantity = int(request.POST.get('received_quantity', 0))
            if received_quantity > 0:
                ProductStock.objects.create(product=product, received_quantity=received_quantity)
                product.limit_quantity += received_quantity
                product.save()
                messages.success(request, f'Количество продукта {product.product_name_rus} обновлено на {received_quantity}.')
            else:
                messages.error(request, 'Количество должно быть больше нуля.')
        except ValueError:
            messages.error(request, 'Неверное количество. Пожалуйста, введите число.')
            logger.error(f"Invalid quantity entered for product {product.product_name_rus} (ID: {product_id}) by user {request.user.id}")
    return redirect('limited_products')
