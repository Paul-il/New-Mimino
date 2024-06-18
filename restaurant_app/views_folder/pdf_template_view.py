from django.shortcuts import render, get_object_or_404
from restaurant_app.models.orders import Order

def pdf_template_view(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    order_items = order.order_items.all()

    for item in order_items:
        item.total_price = item.quantity * item.product.product_price

    total_price = sum(item.total_price for item in order_items)
    context = {'order': order, 'order_items': order_items, 'total_price': total_price}
    return render(request, 'pdf_template.html', context)
