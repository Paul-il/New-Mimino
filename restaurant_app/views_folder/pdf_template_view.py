from django.shortcuts import render, get_object_or_404
from restaurant_app.models.orders import Order

def pdf_template_view(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    total_price = sum(
            order_item.quantity * order_item.product.product_price
            for order_item in order.order_items.all()
        )
    context = {'order': order, 'total_price': total_price}
    return render(request, 'pdf_template.html', context)
