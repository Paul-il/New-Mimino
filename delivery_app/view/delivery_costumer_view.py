from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from ..models import DeliveryCustomer, DeliveryOrder, DeliveryCartItem
import logging

logger = logging.getLogger(__name__)

def customer_orders_view(request):
    search_query = request.GET.get('search', '')

    if search_query:
        customers = DeliveryCustomer.objects.filter(delivery_phone_number__icontains=search_query)
    else:
        customers = DeliveryCustomer.objects.all()
    
    total_customers = customers.count()
    orders = DeliveryOrder.objects.select_related('customer').all()
    
    context = {
        'customers': customers,
        'total_customers': total_customers,
        'orders': orders,
        'search_query': search_query,
    }
    
    return render(request, 'customer_orders.html', context)

def customer_detail_view(request, customer_id):
    customer = get_object_or_404(DeliveryCustomer, pk=customer_id)
    orders = DeliveryOrder.objects.filter(customer=customer)
    total_order_amount = sum(order.total_amount for order in orders if order.total_amount is not None)
    
    context = {
        'customer': customer,
        'orders': orders,
        'total_order_amount': total_order_amount,
    }
    
    return render(request, 'customer_detail.html', context)

def order_detail_view(request, order_id):
    order = get_object_or_404(DeliveryOrder, pk=order_id)
    cart_items = DeliveryCartItem.objects.filter(delivery_order=order)
    
    if not cart_items.exists():
        logger.warning(f"No products found for Order ID: {order.id}")
    else:
        for item in cart_items:
            logger.info(f"Product ID: {item.product.id}, Name: {item.product.product_name_rus}, Quantity: {item.quantity}, Price: {item.product.product_price}")
    
    context = {
        'order': order,
        'cart_items': cart_items,
    }
    
    return render(request, 'order_detail.html', context)

def delete_selected_orders_view(request, customer_id):
    if request.method == 'POST':
        selected_orders = request.POST.getlist('selected_orders')
        for order_id in selected_orders:
            order = get_object_or_404(DeliveryOrder, pk=order_id)
            DeliveryCartItem.objects.filter(delivery_order=order).delete()
            order.delete()
        
        messages.success(request, 'Selected orders have been deleted.')
    return redirect('delivery_app:customer_detail', customer_id=customer_id)

def delete_uncompleted_orders_view(request, customer_id):
    if request.method == 'POST':
        customer = get_object_or_404(DeliveryCustomer, pk=customer_id)
        uncompleted_orders = DeliveryOrder.objects.filter(customer=customer, is_completed=False)
        for order in uncompleted_orders:
            DeliveryCartItem.objects.filter(delivery_order=order).delete()
            order.delete()
        
        messages.success(request, 'All uncompleted orders have been deleted.')
    return redirect('delivery_app:customer_detail', customer_id=customer_id)