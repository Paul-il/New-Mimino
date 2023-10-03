from django.shortcuts import render, get_object_or_404
from ..models import DeliveryOrder, DeliveryCart
from django.http import HttpResponseRedirect

def delivery_pdf_template_view(request, phone_number, order_id):
    order = get_object_or_404(DeliveryOrder, customer__delivery_phone_number=phone_number, id=order_id)
    cart_items = DeliveryCart.objects.filter(delivery_order=order).prefetch_related('delivery_cart_items')
    total_price = sum(
        item.quantity * item.product.product_price
        for cart in order.delivery_carts.all()
        for item in cart.delivery_cart_items.all()
    )

    cart_items = [
        item
        for cart in order.delivery_carts.all()
        for item in cart.delivery_cart_items.all()
    ]

    customer = order.customer
    context = {
        'order': order,
        'cart_items': cart_items,
        'total_price': total_price,
        'customer_name': customer.name,
        'delivery_phone_number': customer.delivery_phone_number,
        'city': customer.city,
        'delivery_street': customer.street,
        'delivery_house_number': customer.house_number,
        'delivery_floor': customer.floor,
        'delivery_apartment_number': customer.apartment_number,
        'delivery_intercom_code': customer.intercom_code,
    }
    return render(request, 'delivery_pdf_template.html', context)
