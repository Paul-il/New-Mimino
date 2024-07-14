from django.shortcuts import get_object_or_404, render, redirect
from django_user_agents.utils import get_user_agent
from django.http import JsonResponse, HttpResponseNotAllowed
from django.db import transaction
from django.db.models import Sum, F
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.utils import timezone
from django.conf import settings
from django.contrib.auth.hashers import check_password
from decimal import Decimal
import logging

from ..models.product import Product, OrderChangeLog
from ..models.tables import Table
from ..models.orders import Order, OrderItem, WaiterOrder, Category, Transaction, PaymentMethod
from ..forms import PasswordForm

logger = logging.getLogger(__name__)

def log_order_change(order, product_name, action, changed_by):
    """Log changes in the order."""
    try:
        OrderChangeLog.objects.create(
            order=order, 
            product_name=product_name, 
            action=action, 
            change_time=timezone.now(),
            changed_by=changed_by
        )
    except Exception as e:
        logger.error(f"Error logging order change: {e}")

def get_cached_product(product_id):
    """Get product from cache or database."""
    product = cache.get(f'product_{product_id}')
    if not product:
        product = get_object_or_404(Product, pk=product_id)
        cache.set(f'product_{product_id}', product, timeout=300)  # кешируем на 5 минут
    return product

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
        if form.is_valid() and check_password(form.cleaned_data['password'], settings.OPERATIONAL_PASSWORD):
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
def confirm_addition_view(request):
    print("Entered confirm_addition_view")
    if request.method == 'POST':
        print("Handling POST request")
        product_id = request.POST.get('product_id')
        quantity = int(request.POST.get('quantity', 1))
        table_id = request.POST.get('table_id')
        print(f"POST Data - product_id: {product_id}, quantity: {quantity}, table_id: {table_id}")

        if request.POST.get('confirm') == 'yes':
            print("Confirmation received")
            table = get_object_or_404(Table, pk=table_id)
            active_order = table.get_active_order()
            print(f"Active order: {active_order}")
            if not active_order:
                num_of_people_str = request.POST.get('num_of_people')
                print(f"Number of people: {num_of_people_str}")
                if num_of_people_str:
                    num_of_people = int(num_of_people_str)
                    room = table.room
                    if num_of_people > room.max_capacity:
                        messages.error(request, f'Количество людей не может превышать максимальную вместимость комнаты {room.max_capacity}.')
                        print(f"Exceeded room capacity: {room.max_capacity}")
                        return redirect('rooms')

                    active_order = Order(
                        table=table,
                        created_by=request.user,
                        num_of_people=num_of_people,
                        table_number=table.table_id
                    )
                    active_order.save()
                    print(f"New order created: {active_order.id}")
                else:
                    messages.error(request, 'Необходимо указать количество посетителей.')
                    print("Number of people not provided")
                    return redirect('rooms')

            product = get_cached_product(product_id)
            print(f"Product retrieved: {product.product_name_rus}")
            order_item, created = active_order.order_items.get_or_create(
                product=product, 
                defaults={'quantity': quantity}
            )
            if not created:
                order_item.quantity += quantity
            order_item.save()
            print(f"Order item saved: {order_item.id}, quantity: {order_item.quantity}")

            log_order_change(order=active_order, product_name=order_item.product.product_name_rus, action='add', changed_by=request.user)
            messages.success(request, f"{quantity} {product.product_name_rus} добавлено в заказ.")
            return redirect('menu', table_id=table_id, category=request.POST.get('category', 'salads'))

        elif request.POST.get('confirm') == 'no':
            messages.info(request, 'Добавление продукта отменено.')
            print("Product addition cancelled")
            return redirect('menu', table_id=table_id, category=request.POST.get('category', 'salads'))

    elif request.method == 'GET':
        print("Handling GET request")
        product_id = request.GET.get('product_id')
        quantity = int(request.GET.get('quantity', 1))
        table_id = request.GET.get('table_id')
        category = request.GET.get('category', 'salads')
        print(f"GET Data - product_id: {product_id}, quantity: {quantity}, table_id: {table_id}, category: {category}")

        product = get_cached_product(product_id)
        print(f"Product retrieved for confirmation: {product.product_name_rus}")
        return render(request, 'confirm_addition.html', {
            'product': product,
            'quantity': quantity,
            'table_id': table_id,
            'category': category
        })

    print("Redirecting to rooms")
    return redirect('rooms')

@login_required
def add_to_cart_view(request, table_id):
    try:
        print(f"Entered add_to_cart_view for table_id: {table_id}")
        table = get_object_or_404(Table, pk=table_id)
        room = table.room
        print(f"Table found: {table_id}, Room: {room.id}")

        if request.method == 'POST':
            print("Handling POST request")
            active_order = table.get_active_order()
            print(f"Active order: {active_order}")

            if not active_order:
                num_of_people_str = request.POST.get('num_of_people')
                print(f"Number of people: {num_of_people_str}")
                if num_of_people_str:
                    num_of_people = int(num_of_people_str)
                    if num_of_people > room.max_capacity:
                        print(f"Exceeded room capacity: {room.max_capacity}")
                        messages.error(request, f'Количество людей не может превышать максимальную вместимость комнаты {room.max_capacity}.')
                        return redirect('rooms')

                    active_order = Order(
                        table=table, 
                        created_by=request.user, 
                        num_of_people=num_of_people,
                        table_number=table.table_id
                    )
                    active_order.save()
                    print(f"New order created: {active_order.id}")
                else:
                    print("Number of people not provided")
                    messages.error(request, 'Необходимо указать количество посетителей.')
                    return redirect('rooms')

            product_id = request.POST.get('product_id')
            print(f"Product ID: {product_id}")
            if product_id:
                quantity = int(request.POST.get('quantity', 1))
                print(f"Quantity: {quantity}")
                product = get_cached_product(product_id)
                print(f"Product: {product.product_name_rus}, Limit: {product.limit_quantity}")

                if quantity > 5 and not request.POST.get('confirm'):
                    print("Quantity > 5, confirmation needed")
                    return render(request, 'confirm_addition.html', {
                        'product': product,
                        'quantity': quantity,
                        'table_id': table_id,
                        'category': request.POST.get('category', 'salads')
                    })

                if request.POST.get('confirm') == 'no':
                    print("Product addition cancelled")
                    return redirect('menu', table_id=table_id, category=request.POST.get('category', 'salads'))

                # Добавление продукта в заказ
                try:
                    if product.has_limit and product.limit_quantity < quantity:
                        print(f"Product limit exceeded: {product.limit_quantity}")
                        messages.error(request, f"Количество лимитированного продукта '{product.product_name_rus}' не может превышать {product.limit_quantity}.")
                        return redirect('menu', table_id=table_id, category=request.POST.get('category', 'salads'))

                    order_item, created = active_order.order_items.get_or_create(
                        product=product,
                        defaults={'quantity': quantity}
                    )
                    if not created:
                        order_item.quantity += quantity
                    order_item.save()
                    print(f"Order item saved: {order_item.id}, Quantity: {order_item.quantity}")

                    product.refresh_from_db()
                    print(f"Product quantity updated: {product.limit_quantity}")

                    if quantity > 1:
                        messages.success(request, f"{quantity} {product.product_name_rus} добавлено в заказ.")
                    else:
                        messages.success(request, f"{product.product_name_rus} добавлено в заказ.")

                    log_order_change(order=active_order, product_name=order_item.product.product_name_rus, action='add', changed_by=request.user)
                    print(f"Order change logged")

                    if product.has_limit:
                        if product.limit_quantity <= 3:
                            print(f"Product quantity below threshold: {product.limit_quantity}")
                            messages.warning(request, f'Внимание: количество продукта "{product.product_name_rus}" ниже порогового уровня. Осталось {product.limit_quantity}.')
                        if not product.is_available:
                            print(f"Product not available")
                            messages.warning(request, f'Внимание: продукт "{product.product_name_rus}" больше не доступен.')

                except ValueError as e:
                    print(f"ValueError: {str(e)}")
                    messages.error(request, str(e))
                print("Redirecting to menu after adding product")
                return redirect('menu', table_id=table_id, category=request.POST.get('category', 'salads'))

        print("Redirecting to menu outside of POST handling")
        return redirect('menu', table_id=table_id, category='salads')

    except Table.DoesNotExist:
        print("Table not found")
        messages.error(request, "Table not found.")
        return redirect('rooms')

@login_required
def calculate_discount_for_product(product_id):
    """Calculate discount for a product."""
    product = Product.objects.get(id=product_id)
    return product.product_price * (product.discount_percentage / 100)

def add_product_to_order(product_id, quantity, active_order, request):
    product = get_cached_product(product_id)
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
    product = order_item.product

    if product.has_limit and product.limit_quantity < 1:
        messages.error(request, f"Количество лимитированного продукта '{product.product_name_rus}' не может быть увеличено.")
        return redirect('cart_detail', order_id)

    order_item.quantity += 1
    order_item.is_delivered = False
    order_item.save()

    product.refresh_from_db()

    log_order_change(order=order_item.order, product_name=order_item.product.product_name_rus, action='add', changed_by=request.user)
    messages.success(request, f"{order_item.product.product_name_rus} добавлено в корзину.")

    if product.has_limit:
        if product.limit_quantity <= 3:
            messages.warning(request, f'Внимание: количество продукта "{product.product_name_rus}" ниже порогового уровня. Осталось {product.limit_quantity}.')
        if not product.is_available:
            messages.warning(request, f'Внимание: продукт "{product.product_name_rus}" больше не доступен.')

    return redirect('cart_detail', order_id)

@login_required
def decrease_product_from_order_view(request, order_id, order_item_id):
    order_item = get_object_or_404(OrderItem, id=order_item_id)
    order = get_object_or_404(Order, id=order_id)

    if order_item.quantity <= 1:
        order_item.delete()
        log_order_change(order, order_item.product.product_name_rus, 'decrease', request.user)
        if not order.order_items.exists():
            order.delete()
            return redirect('rooms')
    else:
        order_item.quantity -= 1
        order_item.save()
        log_order_change(order, order_item.product.product_name_rus, 'decrease', request.user)

    messages.success(request, f"{order_item.product.product_name_rus} убран из заказа.")
    return redirect('cart_detail', order_id)

@login_required
def delete_product_from_order_view(request, order_id, order_item_id):
    order_item = get_object_or_404(OrderItem, id=order_item_id)
    order = get_object_or_404(Order, id=order_id)
    order_item.delete()
    messages.success(request, f"{order_item.product.product_name_rus} удален из заказа.")
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
    """Remove order items with zero quantity."""
    empty_order_items = OrderItem.objects.filter(quantity=0)
    empty_order_items.delete()

@login_required
def empty_order_detail_view(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'empty_order_detail.html', {"order_id": order_id, "order": order})

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
        split_payment = request.POST.get('split_payment')
        cash_amount = Decimal(request.POST.get('cash_amount', '0') or '0')
        card_amount = Decimal(request.POST.get('card_amount', '0') or '0')

        logger.info(f"Received payment method: {payment_method}, split payment: {split_payment}, cash amount: {cash_amount}, card amount: {card_amount}")

        if payment_method in ['cash', 'card', 'mixed']:
            if split_payment:
                order.cash_amount = cash_amount
                order.card_amount = card_amount
                order.payment_method = 'mixed'
                logger.info(f"Order {order.id} paid partially in cash: {cash_amount}, and partially with card: {card_amount}.")
            else:
                if payment_method == 'cash':
                    order.cash_amount = total_price
                    order.card_amount = Decimal('0')
                    logger.info(f"Order {order.id} paid fully in cash.")
                elif payment_method == 'card':
                    order.card_amount = total_price
                    order.cash_amount = Decimal('0')
                    logger.info(f"Order {order.id} paid fully with card.")
                order.payment_method = payment_method

            remaining_total = total_price - (order.cash_amount + order.card_amount)
            logger.info(f"Order {order.id} remaining total after payment: {remaining_total}")

            if remaining_total <= 0:
                order.is_completed = True
                order.payment_processed = True
                logger.info(f"Order {order.id} marked as completed and payment processed.")
                if hasattr(order, 'table'):
                    order.table.is_ordered = False
                    order.table.save()
            order.save()

            if not order.transaction_created:
                create_transaction_for_order(order)
                order.transaction_created = True
                order.save()

            return redirect('tip', table_id=order.table.id if hasattr(order, 'table') else None)

        messages.error(request, 'Неизвестный метод оплаты.')
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

def create_transaction_for_order(order):
    category, _ = Category.objects.get_or_create(name='Table Service Income')

    payment_method = None
    cash_amount = None
    card_amount = None

    if order.payment_method == 'cash':
        payment_method = PaymentMethod.objects.filter(method=PaymentMethod.CASH).first()
        cash_amount = order.total_sum()
    elif order.payment_method == 'card':
        payment_method = PaymentMethod.objects.filter(method=PaymentMethod.CREDIT_CARD).first()
        card_amount = order.total_sum()
    elif order.payment_method == 'mixed':
        payment_method = PaymentMethod.objects.filter(method=PaymentMethod.MIXED).first()
        cash_amount = order.cash_amount
        card_amount = order.card_amount

    Transaction.objects.create(
        type=Transaction.INCOME,
        category=category,
        amount=order.total_sum(),
        cash_amount=cash_amount,
        card_amount=card_amount,
        payment_method=payment_method,
        date=order.updated_at
    )
    logger.info(f"Transaction created for Order {order.id} with amount {order.total_sum()}")

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

    return redirect('add_product_to_waiter_order', product_id=product_id, quantity=quantity)

@login_required
def add_product_to_waiter_order_view(request, product_id, quantity):
    user = request.user
    active_order, created = WaiterOrder.objects.get_or_create(user=user, is_completed=False, defaults={'created_by': user})
    product = get_cached_product(product_id)
    order_item, created = OrderItem.objects.get_or_create(waiter_order=active_order, product=product)

    if not created:
        order_item.quantity += quantity
    else:
        order_item.quantity = quantity
    order_item.save()

    messages.success(request, f"{quantity} {order_item.product.product_name_rus} добавлено в корзину.")
    return redirect('menu_for_waiter', category=request.POST.get('category'))

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
    waiter_order = get_object_or_404(WaiterOrder, id=waiter_order_id, user=request.user, is_completed=False)
    order_item = get_object_or_404(OrderItem, id=order_item_id, waiter_order=waiter_order)
    order_item.delete()
    messages.success(request, f"{order_item.product.product_name_rus} удалено из корзины официанта.")
    if not waiter_order.waiter_order_items.exists():
        waiter_order.delete()
        return redirect('menu_for_waiter', category='salads')
    return redirect('waiter_cart')

@login_required
def delete_waiter_order_and_items_view(request, waiter_order_id):
    waiter_order = get_object_or_404(WaiterOrder, id=waiter_order_id, user=request.user, is_completed=False)
    
    # Удаляем все элементы из заказа
    waiter_order.waiter_order_items.all().delete()
    
    # Удаляем сам заказ
    waiter_order.delete()
    
    messages.success(request, "Заказ и все элементы успешно удалены.")
    return JsonResponse({'status': 'success', 'message': 'Заказ и все элементы успешно удалены.'})

