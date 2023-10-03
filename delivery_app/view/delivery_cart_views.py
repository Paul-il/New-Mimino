from django.shortcuts import render, get_object_or_404, redirect
from django.core.exceptions import ValidationError
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from django.http import HttpResponseBadRequest
from ..models import DeliveryCustomer, DeliveryOrder, DeliveryCart, DeliveryCartItem, Product
from ..forms import ProductQuantityForm
from django.views import View
from django.utils.decorators import method_decorator

def delivery_empty_cart_view(request, delivery_phone_number):
    return render(request, 'delivery_empty_cart.html', {"delivery_phone_number":delivery_phone_number})

def delivery_cart_view(request, delivery_phone_number):
    delivery_customer = get_object_or_404(DeliveryCustomer, delivery_phone_number=delivery_phone_number)

    delivery_order = DeliveryOrder.objects.filter(customer=delivery_customer, is_completed=False).select_related('customer').first()

    if not delivery_order:
        return redirect('delivery_app:delivery_menu', delivery_phone_number=delivery_phone_number, category='salads')

    cart = DeliveryCart.objects.filter(delivery_order=delivery_order).prefetch_related('delivery_cart_items').first()
    if cart:
        cart_items = cart.delivery_cart_items.all()
    else:
        
        return redirect('delivery_app:delivery_empty_cart', delivery_phone_number)

    context = {
        'delivery_phone_number': delivery_phone_number,
        'delivery_order': delivery_order,
        'customer_name': delivery_customer.name,
        'cart_items': cart_items,
        'cart': cart,
    }

    return render(request, 'delivery_cart.html', context)

def delivery_add_to_cart_view(request, delivery_phone_number, category):
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        quantity = int(request.POST.get('quantity'))

        if not product_id or not quantity:
            return redirect('delivery_app:delivery_menu', delivery_phone_number=delivery_phone_number, category=category)

        product = get_object_or_404(Product, id=product_id)
        customer = get_object_or_404(DeliveryCustomer, delivery_phone_number=delivery_phone_number)

        delivery_order, _ = DeliveryOrder.objects.get_or_create(customer=customer, is_completed=False)

        cart, created = DeliveryCart.objects.get_or_create(delivery_order=delivery_order, customer=customer)
        if created:
            cart.save()

        # check if the cart item already exists
        try:
            cart_item = DeliveryCartItem.objects.get(cart=cart, product=product)
            if int(quantity) <= 0:
                return HttpResponseBadRequest('Quantity must be a positive integer')

            cart_item.quantity += int(quantity)
            cart_item.save()
        except DeliveryCartItem.DoesNotExist:
            if int(quantity) <= 0:
                return HttpResponseBadRequest('Quantity must be a positive integer')

            cart_item = DeliveryCartItem(cart=cart, product=product, quantity=quantity, delivery_order=delivery_order)
            cart_item.save()

        cart.save()
        messages.success(request, "Продукт добавлен в корзину.")
        return redirect('delivery_app:delivery_menu', delivery_phone_number=delivery_phone_number, category=category)
    else:
        return redirect('delivery_app:delivery_menu', delivery_phone_number=delivery_phone_number, category=category)

def delivery_increase_product_view(request, delivery_phone_number, product_id):
    delivery_order = DeliveryOrder.objects.filter(customer__delivery_phone_number=delivery_phone_number).order_by('-id').first()
    if not delivery_order:
        raise Http404("No DeliveryOrder matches the given query.")

    cart = DeliveryCart.objects.get(delivery_order=delivery_order)
    product = get_object_or_404(Product, id=product_id)
    cart_item, created = DeliveryCartItem.objects.get_or_create(cart=cart, product=product)
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    messages.success(request, f"{product.product_name_rus} добавлен в корзину.")
    return redirect('delivery_app:delivery_cart', delivery_phone_number=delivery_phone_number)

def delivery_decrease_product_view(request, delivery_phone_number, product_id):
    delivery_order = DeliveryOrder.objects.filter(customer__delivery_phone_number=delivery_phone_number).order_by('-id').first()
    if not delivery_order:
        raise Http404("No DeliveryOrder matches the given query.")
    product = get_object_or_404(Product, id=product_id)
    cart = DeliveryCart.objects.get(delivery_order=delivery_order)
    cart_item = cart.delivery_cart_items.get(product=product)
    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
    else:
        cart_item.delete()
    messages.success(request, f"{product.product_name_rus} убран из корзины.")
    return redirect('delivery_app:delivery_cart', delivery_phone_number=delivery_phone_number)

def delivery_remove_product_view(request, delivery_phone_number, product_id):
    delivery_customer = get_object_or_404(DeliveryCustomer, delivery_phone_number=delivery_phone_number)
    delivery_order = DeliveryOrder.objects.filter(customer=delivery_customer, is_completed=False).first()
    cart_item = get_object_or_404(DeliveryCartItem, cart=delivery_order.delivery_carts.first(), product_id=product_id)
    cart_item.delete()
    messages.success(request, f"{cart_item.product.product_name_rus} удалено из корзины")
    return redirect('delivery_app:delivery_cart', delivery_phone_number=delivery_phone_number)