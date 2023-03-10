from django.shortcuts import get_object_or_404, render, redirect
from django.http import JsonResponse
from django.db.models import Sum, F
from django.contrib import messages

from ..models.product import Product
from ..models.tables import Table
from ..models.orders import OrderItem, Order

def add_to_cart_view(request, table_id):
    # Get the current cart from the session, or create a new empty cart if it doesn't exist
    cart = request.session.get('cart', [])

    # Get the table and its active order
    table = get_object_or_404(Table, table_id=table_id)
    active_order = table.orders.filter(is_completed=False).first()

    if request.method == 'POST':
        # If the form has been submitted, get the product ID from the form data and add it to the cart
        product_id = request.POST.get('product_id')
        category = request.POST.get('category')
        quantity = request.POST.get('quantity')
        if product_id:
            # If there is an active order, check if the product is already in the order
            if active_order:
                product = get_object_or_404(Product, pk=product_id)
                order_item = active_order.order_items.filter(product=product).first()

                # If the product is already in the order, increase the quantity
                if order_item:
                    order_item.quantity += int(quantity)
                    order_item.save()
                # If the product is not in the order, add it to the order
                else:
                    order_item = OrderItem.objects.create(order=active_order, product=product)
                    order_item.quantity = int(quantity)
                    order_item.save()
                    messages.success(request, f"Добавилось {quantity} {order_item.product.product_name_rus}.")

                # Update the session to store the new cart
                cart.append(product_id)
                request.session['cart'] = cart

            # If there is no active order, create a new one and add the product to it
            else:
                new_order = Order.objects.create(table=table)
                product = get_object_or_404(Product, pk=product_id)
                OrderItem.objects.create(order=new_order, product=product)

                # Update the session to store the new cart
                cart.append(product_id)
                request.session['cart'] = cart

            # Redirect back to the menu page to prevent the form from being resubmitted
            if table_id:
                return redirect('menu', table_id=table_id, category=category)


    # If the request is not a POST request, redirect back to the menu page
    if table_id:
        return redirect('menu', table_id=table_id, category=request.GET.get('category')) # or pass the default category here as an argument

def increase_product_in_order_view(request, order_id, order_item_id):
    order_item = get_object_or_404(OrderItem, id=order_item_id)
    order_item.quantity += 1
    order_item.save()

    messages.success(request, f"{order_item.product.product_name_rus} на один стало больше.")
    return redirect('order_detail', order_id)


def decrease_product_from_order_view(request, order_id, order_item_id):
    order_item = get_object_or_404(OrderItem, id=order_item_id)
    order_item.quantity = F('quantity') - 1
    order_item.save()
    if order_item.quantity == 0:
        order_item.delete()
    messages.success(request, f"{order_item.product.product_name_rus} на один стало меньше.")
    return redirect('order_detail', order_id)

def delete_product_from_order_view(request, order_id, order_item_id):
    order_item = get_object_or_404(OrderItem, id=order_item_id)
    order_item.delete()
    messages.success(request, f"{order_item.product.product_name_rus} удалено из корзины")
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
    print(order.id)
    #generate_pdf_view(request,order.id)
    order.payment_method = request.POST.get('payment_method')
    order.paid = True
    order.is_completed = True  # Mark the order as completed
    order.save()
    return redirect('tables')

def empty_order_detail_view(request, order_id):
    return render(request, 'pickup_empty_cart.html', {"order_id":order_id})

def order_detail_view(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    order_items = order.order_items.annotate(total_price=F('quantity') * F('product__product_price'))
    total_price = order_items.aggregate(Sum('total_price'))['total_price__sum']

    if order.order_items.count() == 0:
        # Корзина пустая, вернуть ошибку или перенаправить на другую страницу
        order.delete()
        return redirect('tables')

    if request.method == 'POST':
        # Update order with payment information
        payment_method = request.POST.get('payment_method')
        order.payment_method = payment_method
        order.paid = True
        order.save()
        

        # Clear the table associated with the order
        order.table.is_available = True
        order.table.save()

        return redirect('order_confirmation', order_id=order.id)

    return render(request, 'order_detail.html', {'order': order, 'order_items': order_items, 'total_price': total_price})