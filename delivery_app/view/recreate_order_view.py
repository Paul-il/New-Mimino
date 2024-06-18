from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db.models import F
from django.utils import timezone
from ..models import DeliveryOrder, DeliveryCart, DeliveryCartItem

def recreate_order_view(request, order_id):
    original_order = get_object_or_404(DeliveryOrder, pk=order_id)
    customer = original_order.customer
    now = timezone.now()

    # Создаем новый незавершенный заказ
    new_order = DeliveryOrder.objects.create(
        customer=customer,
        courier=original_order.courier,
        is_completed=False,
        delivery_date=now.date(),
        delivery_time=now.time(),
        total_amount=0,  # Будет обновлено позже
    )

    # Создаем новую корзину для нового заказа
    new_cart, created = DeliveryCart.objects.get_or_create(delivery_order=new_order, customer=customer)

    # Копируем товары из оригинального заказа в новую корзину с проверкой лимитов
    original_cart_items = DeliveryCartItem.objects.filter(delivery_order=original_order)
    for item in original_cart_items:
        product = item.product
        quantity = item.quantity

        # Проверка лимитов продукта
        if product.has_limit:
            product.refresh_from_db()
            if product.limit_quantity < quantity:
                messages.error(request, f"Недостаточное количество продукта '{product.product_name_rus}' на складе.")
                new_order.delete()
                new_cart.delete()
                return redirect('delivery_app:order_detail', order_id=order_id)

        DeliveryCartItem.objects.create(
            cart=new_cart,
            delivery_order=new_order,
            product=product,
            quantity=quantity,
        )

        if product.has_limit:
            product.limit_quantity = F('limit_quantity') - quantity
            product.save(update_fields=['limit_quantity'])
            product.refresh_from_db()

    # Обновляем общую сумму нового заказа
    new_order.total_amount = new_cart.get_total()
    new_order.save()

    return redirect('delivery_app:delivery_cart', delivery_phone_number=customer.delivery_phone_number, delivery_type='delivery')

