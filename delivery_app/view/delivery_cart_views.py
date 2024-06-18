from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Sum, F
from django.http import Http404
from ..models import DeliveryCustomer, DeliveryOrder, DeliveryCart, DeliveryCartItem, Product

def delivery_empty_cart_view(request, delivery_phone_number, delivery_type):
    return render(request, 'delivery_empty_cart.html', {"delivery_phone_number": delivery_phone_number, "delivery_type": delivery_type})

def delivery_cart_view(request, delivery_phone_number, delivery_type):
    delivery_customer = get_object_or_404(DeliveryCustomer, delivery_phone_number=delivery_phone_number)
    delivery_order = DeliveryOrder.objects.filter(customer=delivery_customer, is_completed=False).select_related('customer').first()

    if not delivery_order:
        return redirect('delivery_app:delivery_menu', delivery_phone_number=delivery_phone_number, delivery_type=delivery_type, category='salads')

    cart = DeliveryCart.objects.filter(delivery_order=delivery_order).prefetch_related('delivery_cart_items').first()
    if cart:
        cart_items = cart.delivery_cart_items.all()
    else:
        return redirect('delivery_app:delivery_empty_cart', delivery_phone_number, delivery_type)

    context = {
        'delivery_phone_number': delivery_phone_number,
        'delivery_type': delivery_type,
        'delivery_order': delivery_order,
        'customer_name': delivery_customer.name,
        'cart_items': cart_items,
        'cart': cart,
    }

    return render(request, 'delivery_cart.html', context)

def delivery_add_to_cart_view(request, delivery_phone_number, category, delivery_type):
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        quantity = int(request.POST.get('quantity'))

        if not product_id or not quantity:
            return redirect('delivery_app:delivery_menu', delivery_phone_number=delivery_phone_number, category=category, delivery_type=delivery_type)

        product = get_object_or_404(Product, id=product_id)
        customer = get_object_or_404(DeliveryCustomer, delivery_phone_number=delivery_phone_number)
        delivery_order = DeliveryOrder.objects.filter(customer=customer, is_completed=False).first()
        cart, created = DeliveryCart.objects.get_or_create(delivery_order=delivery_order, customer=customer)
        if created:
            cart.save()

        if product.has_limit:
            existing_quantity = DeliveryCartItem.objects.filter(cart=cart, product=product).aggregate(Sum('quantity'))['quantity__sum'] or 0
            if existing_quantity + quantity > product.limit_quantity:
                messages.error(request, f"Количество лимитированного продукта '{product.product_name_rus}' не может превышать {product.limit_quantity}.")
                return redirect('delivery_app:delivery_menu', delivery_phone_number=delivery_phone_number, category=category, delivery_type=delivery_type)

        cart_item, created = DeliveryCartItem.objects.get_or_create(cart=cart, product=product, defaults={'quantity': quantity, 'delivery_order': delivery_order})
        if not created:
            cart_item.quantity += quantity
            cart_item.save()

        if product.has_limit:
            product.limit_quantity = F('limit_quantity') - quantity
            product.save(update_fields=['limit_quantity'])
            product.refresh_from_db()

        if quantity > 1:
            messages.success(request, f"{quantity} {product.product_name_rus} добавлено в корзину.")
        else:
            messages.success(request, f"{product.product_name_rus} добавлен в корзину.")

        cart.save()
        return redirect('delivery_app:delivery_menu', delivery_phone_number=delivery_phone_number, category=category, delivery_type=delivery_type)
    else:
        return redirect('delivery_app:delivery_menu', delivery_phone_number=delivery_phone_number, category=category, delivery_type=delivery_type)

def delivery_increase_product_view(request, delivery_phone_number, product_id, delivery_type):
    delivery_order = DeliveryOrder.objects.filter(customer__delivery_phone_number=delivery_phone_number).order_by('-id').first()
    if not delivery_order:
        raise Http404("No DeliveryOrder matches the given query.")
    
    cart, created = DeliveryCart.objects.get_or_create(delivery_order=delivery_order, customer=delivery_order.customer)
    product = get_object_or_404(Product, id=product_id)
    
    if product.has_limit:
        existing_quantity = DeliveryCartItem.objects.filter(cart=cart, product=product).aggregate(Sum('quantity'))['quantity__sum'] or 0
        if existing_quantity + 1 > product.limit_quantity:
            messages.error(request, f"Количество лимитированного продукта '{product.product_name_rus}' не может превышать {product.limit_quantity}.")
            return redirect('delivery_app:delivery_cart', delivery_phone_number=delivery_phone_number, delivery_type=delivery_type)
    
    cart_item, created = DeliveryCartItem.objects.get_or_create(cart=cart, product=product, defaults={'quantity': 1, 'delivery_order': delivery_order})
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    
    if product.has_limit:
        product.limit_quantity = F('limit_quantity') - 1
        product.save(update_fields=['limit_quantity'])
        product.refresh_from_db()

    if cart_item.quantity > 1:
        messages.success(request, f"{cart_item.quantity} {product.product_name_rus} добавлено в корзину. Осталось: {product.limit_quantity}.")
    else:
        messages.success(request, f"{product.product_name_rus} добавлен в корзину. Осталось: {product.limit_quantity}.")
    return redirect('delivery_app:delivery_cart', delivery_phone_number=delivery_phone_number, delivery_type=delivery_type)

def delivery_decrease_product_view(request, delivery_phone_number, product_id, delivery_type):
    delivery_order = DeliveryOrder.objects.filter(customer__delivery_phone_number=delivery_phone_number).order_by('-id').first()
    if not delivery_order:
        raise Http404("No DeliveryOrder matches the given query.")
    
    product = get_object_or_404(Product, id=product_id)
    cart = get_object_or_404(DeliveryCart, delivery_order=delivery_order)
    cart_item = cart.delivery_cart_items.get(product=product)
    
    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
    else:
        cart_item.delete()
        if not cart.delivery_cart_items.exists():
            if product.has_limit:
                product.limit_quantity = F('limit_quantity') + 1
                product.save(update_fields=['limit_quantity'])
            cart.delete()
            return redirect('rooms')
    
    if product.has_limit:
        product.limit_quantity = F('limit_quantity') + 1
        product.save(update_fields=['limit_quantity'])
    
    if cart_item.quantity > 1:
        messages.success(request, f"{cart_item.quantity} {product.product_name_rus} убрано из корзины.")
    else:
        messages.success(request, f"{product.product_name_rus} убран из корзины.")
    return redirect('delivery_app:delivery_cart', delivery_phone_number=delivery_phone_number, delivery_type=delivery_type)

def delivery_remove_product_view(request, delivery_phone_number, product_id, delivery_type):
    delivery_customer = get_object_or_404(DeliveryCustomer, delivery_phone_number=delivery_phone_number)
    delivery_order = DeliveryOrder.objects.filter(customer=delivery_customer, is_completed=False).first()
    cart_item = get_object_or_404(DeliveryCartItem, cart=delivery_order.delivery_carts.first(), product_id=product_id)
    
    if cart_item.product.has_limit:
        cart_item.product.limit_quantity = F('limit_quantity') + cart_item.quantity
        cart_item.product.save(update_fields=['limit_quantity'])
    
    cart_item.delete()
    if not cart_item.cart.delivery_cart_items.exists():
        cart_item.cart.delete()
        delivery_order.delete()
        return redirect('rooms')
    
    messages.success(request, f"{cart_item.product.product_name_rus} удален из корзины.")
    return redirect('delivery_app:delivery_cart', delivery_phone_number=delivery_phone_number, delivery_type=delivery_type)

