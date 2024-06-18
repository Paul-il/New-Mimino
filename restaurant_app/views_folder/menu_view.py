# menu_view.py
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.contrib import messages

from ..forms import ProductQuantityForm, OrderItemForm
from ..models.orders import Order, OrderItem, WaiterOrder
from ..models.product import Product
from ..models.tables import Table

CATEGORIES = {
    'salads': 'Салаты',
    'first_dishes': 'Закуски',
    'khachapuri': 'Хачапури',
    'bakery': 'Выпечка',
    'soups': 'Супы',
    'khinkali': 'Хинкали',
    'meat_dishes': 'Мясные блюда',
    'grill_meat': 'Мясо на огне',
    'garnish': 'Гарниры',
    'dessert': 'Десерты',
    'soft_drinks': 'Легкие напитки',
    'beer': 'Пиво',
    'wine': 'Вино',
    'vodka': 'Водка',
    'cognac': 'Коньяк',
    'whisky': 'Виски',
    'dessert_drinks': 'Горячие напитки',
    'own_alc': 'Свой алкоголь',
    'banket': 'Банкет',
}

@login_required
def menu_view(request, table_id, category):
    table = get_object_or_404(Table, table_id=table_id)
    
    # Сортируем продукты по имени
    products = Product.objects.filter(category=category).order_by('product_name_rus')
    
    product_quantity_form = ProductQuantityForm()
    active_order = table.orders.filter(is_completed=False).first()
    active_order_pk = active_order.pk if active_order else None
    order_id = request.GET.get('order_id')

    context = {
        'table': table,
        'active_order': active_order,
        'products': products,
        'category': category,
        'order_id': order_id,
        'product_quantity_form': product_quantity_form,
        'CATEGORIES': CATEGORIES,
        'active_order_pk': active_order_pk,
        'has_active_orders': bool(active_order),
    }

    return render(request, 'menu.html', context=context)

@login_required
def menu_for_waiter_view(request, category):
    product_quantity_form = ProductQuantityForm()
    active_order = WaiterOrder.objects.filter(user=request.user, is_completed=False).first()
    
    # Если активного заказа нет, создаем новый
    if not active_order:
        active_order = WaiterOrder.objects.create(user=request.user, created_by=request.user)

    active_order_pk = active_order.pk if active_order else None

    products = Product.objects.filter(category=category)

    context = {
        'user': request.user,
        'active_order': active_order,
        'products': products,
        'category': category,
        'product_quantity_form': product_quantity_form,
        'CATEGORIES': CATEGORIES,
        'active_order_pk': active_order_pk,
        'has_active_orders': bool(active_order),
    }

    context['order_item_form'] = OrderItemForm()
    return render(request, 'menu_for_waiter.html', context=context)
