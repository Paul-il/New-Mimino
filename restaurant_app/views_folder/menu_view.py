from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.shortcuts import render

from ..forms import ProductQuantityForm, OrderItemForm
from ..models.product import Product
from ..models.tables import Table
from ..models.orders import Order, OrderItem

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
    'drinks': 'Напитки',
    'dessert': 'Десерты',
    'sales': 'Акции',
}

@login_required
def menu_view(request, table_id, category):
    # If the table_id starts with "pickup-", extract the pickup order ID from the string

    table = get_object_or_404(Table, table_id=table_id)
    product_quantity_form = ProductQuantityForm()
    # Get the active order for the table or the pickup order

    active_order = table.orders.filter(is_completed=False).first()

    # Get the category filter from the query parameters or use the default value
    category = request.GET.get('category', 'salads')

    # Get the products for the selected category
    products = Product.objects.filter(category=category)

    # Get the order ID from the query parameters
    order_id = request.GET.get('order_id')

    # Define the context for the template
    context = {
        'table': table,
        'active_order': active_order,
        'products': products,
        'category': category,
        'order_id': order_id,
        'product_quantity_form': product_quantity_form,
        'CATEGORIES': CATEGORIES,
    }

    # If the request is a POST request, add the new order item to the cart
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
            active_order = Order.objects.create(table=table)
            order_item, _ = OrderItem.objects.get_or_create(order=active_order, product=product)
            if quantity is not None:
                order_item.quantity += int(quantity)

            order_item.save()

        # Set the context variable for the active order after the update
        context['active_order'] = active_order
    if table:
        context['order_id'] = f'{table_id}?order_id={request.GET.get("order_id")}&category={category}'

    # Add the context variable for the form to add a new order item
    context['order_item_form'] = OrderItemForm()
    # Create a form to search for products   

    # Render the menu page with the selected products and other data
    return render(request, 'menu.html', context=context)
