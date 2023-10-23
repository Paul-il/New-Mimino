from django.shortcuts import get_object_or_404, render, redirect
from django.http import JsonResponse
from django.db.models import Sum, F
from django.contrib import messages
from django.contrib.auth.models import User

from ..models.product import Product
from ..models.tables import Table
from ..models.orders import OrderItem, Order, WaiterOrder

def add_to_cart_view(request, table_id):
    if request.method != 'POST':
        return redirect('menu', table_id=table_id, category=request.GET.get('category'))

    cart = request.session.get('cart', [])
    table = get_object_or_404(Table, table_id=table_id)
    active_order = table.orders.filter(is_completed=False).first()

    product_id = request.POST.get('product_id')
    category = request.POST.get('category')
    quantity = int(request.POST.get('quantity', 1))

    if not product_id:
        messages.error(request, "Выбран неверный продукт.")
        return redirect('menu', table_id=table_id, category=category)

    add_product_to_order(product_id, quantity, active_order, table, request.user, request)

    cart.append(product_id)
    request.session['cart'] = cart

    return redirect('menu', table_id=table_id, category=category)


def add_product_to_order(product_id, quantity, active_order, table, user, request):
    product = get_object_or_404(Product, pk=product_id)

    if active_order:
        order_item, created = active_order.order_items.get_or_create(product=product, defaults={'quantity': quantity})

        if not created:
            order_item.quantity += quantity
            order_item.save()

        messages.success(request, f"{quantity} {order_item.product.product_name_rus} добавлено в корзину.")
    else:
        new_order = Order.objects.create(table=table, created_by=user, table_number=table.table_id)
        order_item = OrderItem.objects.create(order=new_order, product=product, quantity=quantity)  # Save the created order item to the variable
        messages.success(request, f"{quantity} {order_item.product.product_name_rus} добавлено в корзину.")


def increase_product_in_order_view(request, order_id, order_item_id):
    order_item = get_object_or_404(OrderItem, id=order_item_id)
    order_item.quantity += 1
    order_item.save()

    messages.success(request, f"{order_item.product.product_name_rus} Добавили в корзину.")
    return redirect('order_detail', order_id)


def decrease_product_from_order_view(request, order_id, order_item_id):
    order_item = get_object_or_404(OrderItem, id=order_item_id)
    if order_item.quantity <= 1:
        if OrderItem.objects.filter(order_id=order_id).count() == 1:  # если в заказе только один элемент
            Order.objects.get(id=order_id).delete()
            return redirect('rooms')
        else:
            order_item.delete()
    else:
        order_item.quantity = F('quantity') - 1
        order_item.save()


    messages.success(request, f"{order_item.product.product_name_rus} Убрали из корзины.")
    return redirect('order_detail', order_id)


def delete_product_from_order_view(request, order_id, order_item_id):
    order_item = get_object_or_404(OrderItem, id=order_item_id)
    order_item.delete()
    messages.success(request, f"{order_item.product.product_name_rus} удалено из корзины")

    # Проверяем, есть ли другие элементы в заказе
    order = get_object_or_404(Order, id=order_id)
    if not order.order_items.exists():  # Если нет других элементов в заказе
        order.delete()  # Удаляем заказ
        return redirect('rooms')  # Перенаправляем на страницу со списком комнат или на другую страницу по вашему усмотрению

    return redirect('order_detail', order_id)


def get_order_item_quantity_view(request, order_id, order_item_id):
    order_item = OrderItem.objects.get(order__id=order_id, id=order_item_id)
    data = {order_item.quantity}
    return JsonResponse(data, safe=False)


def remove_empty_order_items():
    empty_order_items = OrderItem.objects.filter(quantity=0)
    empty_order_items.delete()


def pay_order_view(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    order.payment_method = request.POST.get('payment_method')
    order.paid = True
    order.is_completed = True
    order.comments = ''
    order.save()
    return redirect('rooms')


def empty_order_detail_view(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'empty_order_detail.html', {"order_id": order_id, "order": order})

def order_detail_view(request, order_id):
    orders = Order.objects.filter(id=order_id, is_completed=False)
    all_users = User.objects.filter(is_active=True)

    if not orders.exists():
        return empty_order_detail_view(request, order_id)

    order = orders.first()
    table = order.table  # Получите стол, связанный с заказом
    order_items = order.order_items.annotate(total_price=F('quantity') * F('product__product_price'))
    total_price = order_items.aggregate(Sum('total_price'))['total_price__sum']

    if order.order_items.count() == 0:
        # Корзина пустая, вернуть ошибку или перенаправить на другую страницу
        order.delete()
        return redirect('rooms')

    if request.method == 'POST':
        # Update order with payment information
        payment_method = request.POST.get('payment_method')
        order.payment_method = payment_method
        order.paid = True
        order.save()

        # Clear the table associated with the order
        order.table.is_available = True
        order.table.save()

        return redirect('order_detail', order_id=order.id)

    return render(request, 'order_detail.html', {
        'order': order, 
        'order_items': order_items, 
        'total_price': total_price,
        'table': table,
        'all_users': all_users,})


#############################################################################################################

def add_to_waiter_cart_view(request):
    if request.method != 'POST':
        return redirect('menu_for_waiter', category=request.GET.get('category'))

    product_id = request.POST.get('product_id')
    category = request.POST.get('category')
    quantity = int(request.POST.get('quantity', 1))

    if not product_id:
        messages.error(request, "Выбран неверный продукт.")
        return redirect('menu_for_waiter', category=category)

    # Просто передайте product_id и quantity в функцию add_product_to_waiter_order
    add_product_to_waiter_order(product_id, quantity, request)

    return redirect('menu_for_waiter', category=category)


def add_product_to_waiter_order(product_id, quantity, request):
    user = request.user
    active_order = WaiterOrder.objects.filter(user=request.user, is_completed=False).first()

    # Если у официанта нет активного заказа, создаем новый
    if not active_order:
        active_order = WaiterOrder.objects.create(user=user, created_by=user)

    product = get_object_or_404(Product, pk=product_id)
    order_item, created = OrderItem.objects.get_or_create(waiter_order=active_order, product=product)

    # Обновляем количество товара в заказе
    if not created:
        order_item.quantity += quantity
    else:
        order_item.quantity = quantity
    order_item.save()

    messages.success(request, f"{quantity} {order_item.product.product_name_rus} добавлено в корзину.")
    category = request.POST.get('category')
    return redirect('menu_for_waiter', category=category)


def waiter_cart_view(request):
    # Получаем активный заказ официанта
    active_order = WaiterOrder.objects.filter(user=request.user, is_completed=False).first()

    # Если у официанта нет активного заказа, перенаправляем его обратно к меню
    if not active_order:
        messages.warning(request, "Ваша корзина пуста.")
        return redirect('menu_for_waiter', category='salads')

    # Получаем все элементы заказа для этого активного заказа
    order_items = active_order.waiter_order_items.all()

    # Вычисляем общую стоимость заказа
    total_price = sum(item.product.product_price * item.quantity for item in order_items)

    context = {
        'active_order': active_order,
        'order_items': order_items,
        'total_price': total_price,
    }

    return render(request, 'waiter_cart.html', context=context)


def delete_product_from_waiter_order_view(request, waiter_order_id, order_item_id):
    waiter_order = get_object_or_404(WaiterOrder, id=waiter_order_id)
    order_item = get_object_or_404(OrderItem, id=order_item_id, waiter_order=waiter_order)
    order_item.delete()
    messages.success(request, f"{order_item.product.product_name_rus} удалено из корзины официанта.")
    return redirect('waiter_cart')
