from django.shortcuts import render, get_object_or_404
from pickup_app.models import PickupOrder, CartItem
from django.db import models

def pickup_pdf_template_view(request, phone_number, order_id):
    order = get_object_or_404(PickupOrder, phone=phone_number, id=order_id)
    cart_items = CartItem.objects.filter(cart__pickup_order=order)
    total = order.carts.aggregate(total=models.Sum('total_price'))['total']
    total_price = sum(
    item.quantity * item.product.product_price
    for cart in order.carts.all()
    for item in cart.cart_items.all()
    )

    context = {'order': order, 'cart_items': cart_items, 'total_price': total_price}
    return render(request, 'pickup_pdf_template.html', context)
