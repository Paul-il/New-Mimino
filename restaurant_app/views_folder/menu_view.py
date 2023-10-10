from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from ..forms import ProductQuantityForm, OrderItemForm
from ..models.orders import Order, OrderItem
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
    'wine' :'Вино',
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
    product_quantity_form = ProductQuantityForm()
    active_order = table.orders.filter(is_completed=False).first()
    active_order_pk = table.orders.filter(is_completed=False).first().pk if table.orders.filter(is_completed=False).exists() else None


    products = Product.objects.filter(category=category)
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

    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        quantity = request.POST.get('quantity')
        product = get_object_or_404(Product, pk=product_id)

        if active_order:
            # Add the product to the existing active order
            order_item, _ = OrderItem.objects.get_or_create(order=active_order, product=product)
            if quantity is not None:
                order_item.quantity += int(quantity)

            order_item.save()

        else:
            # Create a new active order and add the product to it
            active_order = Order.objects.create(table=table, created_by=request.user, table_number=table.table_id)
            order_item, _ = OrderItem.objects.get_or_create(order=active_order, product=product)
            if quantity is not None:
                order_item.quantity = int(quantity)
            order_item.save()


        # Set the context variable for the active order after the update
        context['active_order'] = active_order

        # Get the category filter from the POST parameters or use the default value
        category = request.POST.get('category', 'salads')

        # Add the category to the parameters of the redirect
        redirect_url = reverse('menu', kwargs={'table_id': table_id, 'category': category})
        if order_id:
            redirect_url += f'?order_id={order_id}'
        return redirect(redirect_url)

    if table:
        context['order_id'] = f'{table_id}?order_id={order_id}&category={category}'

    context['order_item_form'] = OrderItemForm()

    return render(request, 'menu.html', context=context)
