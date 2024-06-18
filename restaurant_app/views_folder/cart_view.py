from django.shortcuts import get_object_or_404, render, redirect
from django_user_agents.utils import get_user_agent
from django.http import JsonResponse, HttpResponseNotAllowed
from django.db.models import Sum, F
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.utils import timezone
from ..models.product import Product, OrderChangeLog
from ..models.tables import Table
from ..models.orders import OrderItem, Order, WaiterOrder
from ..forms import PasswordForm
from django.conf import settings
from asgiref.sync import sync_to_async
from decimal import Decimal


def log_order_change(order, product_name, action, changed_by):
    """Логирует изменения в заказе."""
    try:
        OrderChangeLog.objects.create(
            order=order, 
            product_name=product_name, 
            action=action, 
            change_time=timezone.now(),
            changed_by=changed_by
        )
    except Exception as e:
        print(f"Ошибка при логировании изменения заказа: {e}")

@login_required
def confirm_order_view(request, order_id):
    order = get_object_or_404(Order, pk=order_id)
    order.is_confirmed = True
    order.save()
    return redirect('order_detail', order_id=order.id)

@login_required
def password_check_view(request, order_id, action, order_item_id=None):
    order = get_object_or_404(Order, pk=order_id)
    is_admin = request.user.is_superuser

    if is_admin or (not order.is_confirmed and not order.is_bill_printed):
        return perform_order_action(request, order_id, action, order_item_id)

    if request.method == 'POST':
        form = PasswordForm(request.POST)
        if form.is_valid() and form.cleaned_data['password'] == settings.OPERATIONAL_PASSWORD:
            return perform_order_action(request, order_id, action, order_item_id)
        else:
            messages.error(request, 'Неверный операционный пароль.')
    else:
        form = PasswordForm()
    
    return render(request, 'password_check.html', {
        'form': form,
        'order_id': order_id,
        'order_item_id': order_item_id,
        'action': action
    })

@login_required
def perform_order_action(request, order_id, action, order_item_id):
    if action == 'decrease':
        return decrease_product_from_order_view(request, order_id, order_item_id)
    elif action == 'delete':
        return delete_product_from_order_view(request, order_id, order_item_id)
    else:
        messages.error(request, 'Неизвестное действие.')
        return redirect('some_default_view')

@login_required
def add_to_cart_view(request, table_id):
    table = get_object_or_404(Table, pk=table_id)
    room = table.room

    if request.method == 'POST':
        active_order = table.get_active_order()

        if not active_order:
            num_of_people_str = request.POST.get('num_of_people')
            if num_of_people_str:
                num_of_people = int(num_of_people_str)
                if num_of_people > room.max_capacity:
                    messages.error(request, f'Количество людей не может превышать максимальную вместимость комнаты {room.max_capacity}.')
                    return redirect('rooms')

                active_order = Order.objects.create(
                    table=table, 
                    created_by=request.user, 
                    num_of_people=num_of_people,
                    table_number=table.table_id
                )
            else:
                messages.error(request, 'Необходимо указать количество посетителей.')
                return redirect('rooms')

        product_id = request.POST.get('product_id')
        if product_id:
            quantity = int(request.POST.get('quantity', 1))
            product = get_object_or_404(Product, pk=product_id)
            order_item, created = active_order.order_items.get_or_create(
                product=product, 
                defaults={'quantity': quantity}
            )
            if not created:
                order_item.quantity = F('quantity') + quantity
                order_item.save(update_fields=['quantity'])
            messages.success(request, f"{quantity} {order_item.product.product_name_rus} добавлено в заказ.")
            log_order_change(order=active_order, product_name=order_item.product.product_name_rus, action='add', changed_by=request.user)

        return redirect('menu', table_id=table_id, category=request.POST.get('category', 'salads'))

    return redirect('menu', table_id=table_id, category='salads')

@login_required
def calculate_discount_for_product(product_id):
    product = Product.objects.get(id=product_id)
    return product.product_price * (product.discount_percentage / 100)

@login_required
def add_product_to_order(product_id, quantity, active_order, request):
    product = get_object_or_404(Product, pk=product_id)
    discount_amount = calculate_discount_for_product(product_id)
    order_item, created = active_order.order_items.get_or_create(
        product=product, 
        defaults={'quantity': quantity, 'discount': discount_amount}
    )
    if not created:
        order_item.quantity += quantity
        order_item.discount = discount_amount
        order_item.save()
    messages.success(request, f"{quantity} {order_item.product.product_name_rus} добавлено в заказ.")
    log_order_change(order=active_order, product_name=order_item.product.product_name_rus, action='add')

@login_required
def increase_product_in_order_view(request, order_id, order_item_id):
    order_item = get_object_or_404(OrderItem, id=order_item_id)
    order_item.quantity += 1
    order_item.is_delivered = False
    order_item.save()
    log_order_change(order=order_item.order, product_name=order_item.product.product_name_rus, action='add', changed_by=request.user)
    messages.success(request, f"{order_item.product.product_name_rus} добавлено в корзину.")
    return redirect('cart_detail', order_id)

@login_required
def decrease_product_from_order_view(request, order_id, order_item_id):
    order_item = get_object_or_404(OrderItem, id=order_item_id)
    order = get_object_or_404(Order, id=order_id)

    if order_item.quantity <= 1:
        if OrderItem.objects.filter(order_id=order_id).count() == 1:
            Order.objects.get(id=order_id).delete()
            return redirect('rooms')
        else:
            order_item.delete()
            log_order_change(order, order_item.product.product_name_rus, 'decrease', request.user)
    else:
        order_item.quantity -= 1
        order_item.save()
        log_order_change(order, order_item.product.product_name_rus, 'decrease', request.user)

    messages.success(request, f"{order_item.product.product_name_rus} убрали из корзины.")
    return redirect('cart_detail', order_id)

@login_required
def delete_product_from_order_view(request, order_id, order_item_id):
    order_item = get_object_or_404(OrderItem, id=order_item_id)
    order = get_object_or_404(Order, id=order_id)
    order_item.delete()
    messages.success(request, f"{order_item.product.product_name_rus} удалено из корзины.")
    log_order_change(order, order_item.product.product_name_rus, 'delete', request.user)

    if not order.order_items.exists():
        order.delete()
        return redirect('rooms')

    return redirect('cart_detail', order_id)

@login_required
def get_order_item_quantity_view(request, order_id, order_item_id):
    order_item = OrderItem.objects.get(order__id=order_id, id=order_item_id)
    data = {order_item.quantity}
    return JsonResponse(data, safe=False)

@login_required
def remove_empty_order_items():
    empty_order_items = OrderItem.objects.filter(quantity=0)
    empty_order_items.delete()

@login_required
def empty_order_detail_view(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'empty_order_detail.html', {"order_id": order_id, "order": order})


from decimal import Decimal

@login_required
def order_detail_view(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    all_users = User.objects.filter(is_active=True)
    user_agent = get_user_agent(request)
    is_not_desktop = not user_agent.is_pc
    is_admin = request.user.is_superuser

    order_items = order.order_items.annotate(
        discount_amount=F('product__product_price') * F('discount_percentage') / 100,
        final_price=F('product__product_price') - (F('product__product_price') * F('discount_percentage') / 100)
    )

    total_price = sum(item.final_price * item.quantity for item in order_items)
    total_price = Decimal(total_price)

    order_logs = OrderChangeLog.objects.filter(order=order).order_by('change_time')

    if request.method == 'POST':
        payment_method = request.POST.get('payment_method')
        cash_amount = Decimal(request.POST.get('cash_amount', '0') or '0')
        card_amount = Decimal(request.POST.get('card_amount', '0') or '0')

        if payment_method == 'cash':
            order.cash_amount = total_price
            order.card_amount = Decimal('0')
        elif payment_method == 'card':
            order.card_amount = total_price
            order.cash_amount = Decimal('0')
        elif payment_method == 'mixed':
            order.cash_amount = (order.cash_amount or Decimal('0')) + cash_amount
            order.card_amount = (order.card_amount or Decimal('0')) + card_amount

        order.save()

        print(f"Общая сумма: {total_price}₪")
        print(f"Заплачено наличными: {order.cash_amount}₪")
        print(f"Заплачено картой: {order.card_amount}₪")
        remaining_total = total_price - ((order.cash_amount or Decimal('0')) + (order.card_amount or Decimal('0')))
        print(f"Осталось заплатить: {remaining_total}₪")

        if remaining_total <= 0:
            order.is_completed = True
            print(f"Заказ {order.id} закрыт")
            if hasattr(order, 'table'):
                order.table.is_ordered = False
                order.table.save()
            return redirect('tip', table_id=order.table.id)

        return redirect('cart_detail', order_id=order.id)

    return render(request, 'cart_detail.html', {
        'order': order,
        'order_items': order_items,
        'total_price': total_price,
        'partial_cash': order.cash_amount or Decimal('0'),
        'partial_card': order.card_amount or Decimal('0'),
        'remaining_total': total_price - ((order.cash_amount or Decimal('0')) + (order.card_amount or Decimal('0'))),
        'table': order.table if hasattr(order, 'table') else None,
        'all_users': all_users,
        'is_not_desktop': is_not_desktop,
        'is_admin': is_admin,
        'order_logs': order_logs,
    })


@login_required
def apply_discount_view(request):
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])

    for key, value in request.POST.items():
        if key.startswith('discount_percentage_'):
            order_item_id = key.split('_')[-1]
            try:
                discount_percentage = float(value)
                order_item = get_object_or_404(OrderItem, pk=order_item_id)
                order_item.discount_percentage = discount_percentage
                order_item.save()
                print(f"Updated discount for OrderItem {order_item_id}: {discount_percentage}%")
            except (ValueError, OrderItem.DoesNotExist):
                pass

    return redirect('cart_detail', order_id=request.POST.get('order_id'))

@login_required
def update_delivery_status(request, order_item_id):
    order_item = get_object_or_404(OrderItem, id=order_item_id)
    if request.method == "POST":
        order_item.is_delivered = not order_item.is_delivered
        order_item.save()
        return redirect('cart_detail', order_id=order_item.order.id)
    else:
        return HttpResponseNotAllowed(['POST'])

@login_required
def add_to_waiter_cart_view(request):
    if request.method != 'POST':
        return redirect('menu_for_waiter', category=request.GET.get('category'))

    product_id = request.POST.get('product_id')
    category = request.POST.get('category')
    quantity = int(request.POST.get('quantity', 1))

    if not product_id:
        messages.error(request, "Выбран неверный продукт.")
        return redirect('menu_for_waiter', category=category)

    add_product_to_waiter_order(product_id, quantity, request)
    return redirect('menu_for_waiter', category=category)

@login_required
def add_product_to_waiter_order(product_id, quantity, request):
    user = request.user
    active_order, created = WaiterOrder.objects.get_or_create(user=user, is_completed=False, defaults={'created_by': user})
    product = get_object_or_404(Product, pk=product_id)
    order_item, created = OrderItem.objects.get_or_create(waiter_order=active_order, product=product)

    if not created:
        order_item.quantity += quantity
    else:
        order_item.quantity = quantity
    order_item.save()

    messages.success(request, f"{quantity} {order_item.product.product_name_rus} добавлено в корзину.")

@login_required
def waiter_cart_view(request):
    active_order = WaiterOrder.objects.filter(user=request.user, is_completed=False).first()

    if not active_order:
        messages.warning(request, "Ваша корзина пуста.")
        return redirect('menu_for_waiter', category='salads')

    order_items = active_order.waiter_order_items.all()
    total_price = sum(item.product.product_price * item.quantity for item in order_items)

    context = {
        'active_order': active_order,
        'order_items': order_items,
        'total_price': total_price,
    }

    return render(request, 'waiter_cart.html', context=context)

@login_required
def delete_product_from_waiter_order_view(request, waiter_order_id, order_item_id):
    waiter_order = get_object_or_404(WaiterOrder, id=waiter_order_id)
    order_item = get_object_or_404(OrderItem, id=order_item_id, waiter_order=waiter_order)
    order_item.delete()
    messages.success(request, f"{order_item.product.product_name_rus} удалено из корзины официанта.")
    return redirect('waiter_cart')
