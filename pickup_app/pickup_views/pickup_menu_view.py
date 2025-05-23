from restaurant_app.models.product import Product
from ..forms import ProductQuantityForm
from ..models import PickupOrder, Cart, CartItem
from django.shortcuts import render, redirect, get_object_or_404, get_list_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, F

CATEGORIES = {
    'salads': 'Салаты',
    'first_dishes': 'Закуски',
    'khachapuri': 'Хачапури',
    'bakery': 'Выпечка',
    'soups': 'Супы',
    'khinkali': 'Хинкали',
    'meat_dishes': 'Мясные блюда',
    'grill_meat': 'Мясо на огне',
    'garnish':'Гарниры',
    'dessert':'Десерты',
    'soft_drinks': 'Легкие напитки',
    'beer': 'Пиво',
    'wine' :'Вино',
    'vodka': 'Водка',
    'cognac': 'Коньяк',
    'whisky': 'Виски',
    'dessert_drinks': 'Горячие напитки'
}

@login_required
def pickup_menu_view(request, phone_number, category):
    # Сортируем продукты по имени
    products = Product.objects.filter(category=category).order_by('product_name_rus')
    pickup_orders = get_list_or_404(PickupOrder, phone=phone_number)
    pickup_order = pickup_orders[0]
    product_quantity_form = ProductQuantityForm()

    if request.method == 'POST':
        handle_add_to_cart(request, phone_number, pickup_order, category)

    context = {
        'phone_number': phone_number,
        'products': products,
        'category': category,
        'pickup_order': pickup_order,
        'product_quantity_form': product_quantity_form,
        'CATEGORIES': CATEGORIES,
    }

    return render(request, 'pickup_menu.html', context)


def handle_add_to_cart(request, phone_number, pickup_order, category):
    product_id = request.POST.get('product_id')
    quantity = request.POST.get('quantity')
    try:
        quantity = int(quantity)
        if quantity <= 0:
            raise ValueError('Число должно быть больше 0.')
    except ValueError:
        messages.error(request, 'Не верное количество!')
        return redirect('pickup_app:pickup_menu', phone_number=phone_number, category=category)

    product = get_object_or_404(Product, id=product_id)

    if not pickup_order.pk and pickup_order.id is None:
        pickup_order.save()

    cart, created = Cart.objects.get_or_create(pickup_order=pickup_order)

    if not created and not cart.pk:
        cart.save()

    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    product_name = cart_item.product.product_name_rus

    if not created:
        cart_item.quantity += quantity
        cart_item.save()
    else:
        cart_item.quantity = quantity
        cart_item.save()

    # Обновляем количество продукта на складе
    if product.has_limit:
        product.limit_quantity = F('limit_quantity') - quantity
        product.save(update_fields=['limit_quantity'])
        product.refresh_from_db()

    if quantity > 1:
        messages.success(request, f"{quantity} {product_name} было добавлено в корзину.")
    else:
        messages.success(request, f"{product_name} был добавлен в корзину.")

    return redirect('pickup_app:pickup_cart', phone_number=phone_number, category=None)








