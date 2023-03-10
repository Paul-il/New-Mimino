from django.shortcuts import render, get_object_or_404, redirect
from django.core.exceptions import ValidationError
from django.contrib import messages
from django.http import JsonResponse
from ..models import DeliveryCustomer, DeliveryOrder, DeliveryCart, DeliveryCartItem, Product
from ..forms import ProductQuantityForm

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


def delivery_add_to_cart_view(request, delivery_phone_number):
    delivery_customer = get_object_or_404(DeliveryCustomer, delivery_phone_number=delivery_phone_number)
    delivery_order = DeliveryOrder.objects.filter(customer=delivery_customer, is_completed=False).first()
    delivery_category = request.POST.get('category')
    print(delivery_category)

    product_id = request.POST.get('product_id')
    quantity = request.POST.get('quantity')

    try:
        if not product_id.isdigit() or int(product_id) < 1:
            raise ValueError('Invalid product ID')
        if not quantity.isdigit() or int(quantity) < 1:
            raise ValueError('Invalid quantity')

        product = get_object_or_404(Product, id=product_id)
        cart = DeliveryCart.objects.filter(delivery_order=delivery_order).first()

        if cart:
            cart_item = cart.delivery_cart_items.filter(product=product).first()
            if cart_item:
                cart_item.quantity += int(quantity)
                cart_item.save()

            else:
                cart.save()  # Сохраняем объект DeliveryCart перед созданием связанного объекта DeliveryCartItem
                cart_item = DeliveryCartItem.objects.create(product=product, quantity=quantity, cart=cart)
        else:
            cart = DeliveryCart.objects.create(customer=delivery_customer, delivery_order=delivery_order)
            cart.save()  # Сохраняем объект DeliveryCart перед созданием связанного объекта DeliveryCartItem
            cart_item = DeliveryCartItem.objects.create(product=product, quantity=quantity, cart=cart)

        if delivery_category == 'delivery':
            messages.success(request, f"{quantity} {product.product_name_rus} в корзину!")
            return redirect('delivery_app:delivery_cart', delivery_phone_number=delivery_phone_number)
        
        messages.success(request, f"{quantity} {product.product_name_rus} добавлено в корзину!")
        return redirect('delivery_app:delivery_menu', delivery_phone_number=delivery_phone_number, category=product.category)

    except (ValueError, ValidationError) as e:
        return JsonResponse({'error': str(e)}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def delivery_increase_product_view(request, delivery_phone_number, product_id):
    delivery_order = get_object_or_404(DeliveryOrder, customer__delivery_phone_number=delivery_phone_number)
    cart = DeliveryCart.objects.get(delivery_order=delivery_order)
    product = get_object_or_404(Product, id=product_id)
    cart_item, created = DeliveryCartItem.objects.get_or_create(cart=cart, product=product)
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    messages.success(request, f"1 {product.product_name_rus} добавлено в корзину!")
    return redirect('delivery_app:delivery_cart', delivery_phone_number=delivery_phone_number)

def delivery_decrease_product_view(request, delivery_phone_number, product_id):
    delivery_order = get_object_or_404(DeliveryOrder, customer__delivery_phone_number=delivery_phone_number)
    product = get_object_or_404(Product, id=product_id)
    cart = DeliveryCart.objects.get(delivery_order=delivery_order)
    cart_item = cart.delivery_cart_items.get(product=product)
    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
    else:
        cart_item.delete()
    messages.success(request, f"1 {product.product_name_rus} Убрано из корзину!")
    return redirect('delivery_app:delivery_cart', delivery_phone_number=delivery_phone_number)

def delivery_remove_product_view(request, delivery_phone_number, product_id):
    delivery_customer = get_object_or_404(DeliveryCustomer, delivery_phone_number=delivery_phone_number)
    delivery_order = DeliveryOrder.objects.filter(customer=delivery_customer, is_completed=False).first()
    cart_item = get_object_or_404(DeliveryCartItem, cart=delivery_order.delivery_carts.first(), product_id=product_id)
    cart_item.delete()
    messages.success(request, f"{cart_item.product.product_name_rus} удалено из корзины")
    return redirect('delivery_app:delivery_cart', delivery_phone_number=delivery_phone_number)
