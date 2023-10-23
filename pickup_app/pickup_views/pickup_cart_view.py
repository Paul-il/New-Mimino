from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, get_list_or_404
from django.db.models import Sum, F
from django.contrib import messages
from ..models import PickupOrder, Cart, CartItem, OrderItem
from restaurant_app.models.product import Product
from pickup_app.pickup_views.pickup_menu_view import handle_add_to_cart
from django.urls import reverse

def pickup_add_to_cart_view(request, phone_number, category, product_id):
    # Пытаемся найти заказ с данным номером телефона и статусом "NEW"
    pickup_order, created = PickupOrder.objects.get_or_create(
        phone=phone_number, 
        status=PickupOrder.NEW,
        defaults={'name': 'Default Name'}
    )

    # Если заказ со статусом "NEW" не найден, создаем новый заказ
    if not created and pickup_order.status == PickupOrder.COMPLETED:
        pickup_order = PickupOrder.objects.create(phone=phone_number, name='Default Name')

    handle_add_to_cart(request, phone_number, pickup_order, category)
    return redirect(reverse('pickup_app:pickup_menu', kwargs={'phone_number': phone_number, 'category': category}))



def pickup_empty_cart_view(request, phone_number):
    return render(request, 'pickup_empty_cart.html', {"phone_number":phone_number})

@login_required
def pickup_cart_view(request, phone_number, category=None):
    # Получаем объект заказа по номеру телефона
    pickup_order = PickupOrder.objects.filter(phone=phone_number).order_by('-date_created').first()

    # Если заказ не найден, перенаправляем пользователя на страницу пустой корзины
    if not pickup_order:
        return redirect('pickup_app:pickup_empty_cart', phone_number=phone_number)

    # Получаем объект корзины для указанного номера телефона
    cart = get_object_or_404(Cart, pickup_order=pickup_order)

    # Получаем объекты продуктов, которые находятся в корзине
    cart_items = CartItem.objects.filter(cart__pickup_order=pickup_order)

    # Если в корзине нет товаров, перенаправляем на страницу пустой корзины
    if not cart_items.exists():
        return redirect('pickup_app:pickup_empty_cart', phone_number=phone_number)

    # Если в корзине есть товары, продолжаем обработку

    # Получаем объекты заказа, которые находятся в корзине
    order_items = pickup_order.orderitem_set.annotate(total_price=F('quantity') * F('product__product_price'))

    # Вычисляем общую стоимость заказа
    total_price = order_items.aggregate(Sum('total_price'))['total_price__sum']

    # Рендерим шаблон и передаем необходимые переменные в контекст
    return render(request, 'pickup_cart.html', {
        'cart_items': cart_items,
        'order_items': order_items,
        'total_price': total_price,
        'phone_number': phone_number,
        'pickup_order': pickup_order,
        'cart': cart,
    })


@login_required
def get_order_item_quantity_view(request, order_id, order_item_id):
    order_item = OrderItem.objects.get(order__id=order_id, id=order_item_id)
    data = {order_item.quantity}
    return JsonResponse(data, safe=False)

@login_required
def pickup_increase_product_view(request, phone_number, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    # Изменение здесь: получаем последний PickupOrder для данного номера телефона
    pickup_order = PickupOrder.objects.filter(phone=phone_number).order_by('-date_created').first()

    # Проверяем, что заказ был найден
    if not pickup_order:
        messages.error(request, "Заказ не найден.")
        return redirect('pickup_app:pickup_empty_cart', phone_number=phone_number)

    cart = Cart.objects.get(pickup_order=pickup_order)
    cart_item = get_object_or_404(CartItem, cart=cart, product_id=product_id)
    
    cart_item.quantity += 1
    cart_item.save()

    messages.success(request, f"{product.product_name_rus} на один стало больше.")
    return redirect('pickup_app:pickup_cart', phone_number=phone_number, category=None)


@login_required
def pickup_decrease_product_view(request, phone_number, product_id):
    # Получаем объект продукта
    product = get_object_or_404(Product, id=product_id)

    # Извлекаем последний заказ по номеру телефона
    pickup_order = PickupOrder.objects.filter(phone=phone_number).order_by('-date_created').first()

    # Если заказ не найден, перенаправляем пользователя на страницу пустой корзины
    if not pickup_order:
        return redirect('pickup_app:pickup_empty_cart', phone_number=phone_number)

    cart = Cart.objects.get(pickup_order=pickup_order)
    cart_item = get_object_or_404(CartItem, cart=cart, product_id=product_id)

    # Уменьшаем количество товара на 1
    cart_item.quantity -= 1

    # Если количество товара стало равно 0, удаляем элемент из корзины
    if cart_item.quantity == 0:
        cart_item.delete()
    else:
        cart_item.save()

    messages.success(request, f"{product.product_name_rus} на один стало меньше.")
    return redirect('pickup_app:pickup_cart', phone_number=phone_number, category=None)


@login_required
def pickup_remove_product_view(request, phone_number, product_id):
    product = get_object_or_404(Product, id=product_id)

    # Извлекаем последний заказ по номеру телефона
    pickup_order = PickupOrder.objects.filter(phone=phone_number).order_by('-date_created').first()

    # Если заказ не найден, перенаправляем пользователя на страницу пустой корзины
    if not pickup_order:
        return redirect('pickup_app:pickup_empty_cart', phone_number=phone_number)

    cart = Cart.objects.get(pickup_order=pickup_order)
    cart_item = get_object_or_404(CartItem, cart=cart, product_id=product_id)
    cart_item.delete()

    messages.success(request, f"{product.product_name_rus} Был удалён из корзины!")
    return redirect('pickup_app:pickup_cart', phone_number=phone_number, category=None)


@login_required
def pickup_total_price_view(cart_items):
    total_price = 0
    for item in cart_items:
        total_price += item.product.product_price * item.quantity
    return total_price

@login_required
def pay_order(request, id):
    pickup_order = get_object_or_404(PickupOrder, id=id)
    
    # Вычисляем общую сумму заказа
    total_price = 0
    cart = Cart.objects.get(pickup_order=pickup_order)
    for item in cart.cart_items.all():
        total_price += item.product.product_price * item.quantity
        
    # Обновляем total_amount для pickup_order
    pickup_order.total_amount = total_price

    pickup_order.status = 'completed'
    pickup_order.save()

    # Очистка корзины
    #cart.cartitem_set.all().delete()

    return redirect('pickup_app:pickup_cart', phone_number=pickup_order.phone, category='')

