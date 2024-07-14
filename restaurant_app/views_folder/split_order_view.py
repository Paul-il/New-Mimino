from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.contrib import messages
from restaurant_app.models.orders import Order, OrderItem
from restaurant_app.models.tables import Table, VirtualTable

@login_required
@transaction.atomic
def split_order(request, order_id):
    if request.method == 'POST':
        order = get_object_or_404(Order, id=order_id)
        selected_item_ids = request.POST.getlist('selected_items')

        if not selected_item_ids:
            messages.error(request, "Вы не выбрали ни одного продукта для нового счета.")
            return redirect('split_order', order_id=order.id)

        # Создаем виртуальный стол
        virtual_table = VirtualTable.objects.create(
            main_table=order.table,
            created_by=request.user
        )

        # Создаем новый заказ для виртуального стола
        new_order = Order.objects.create(
            table=order.table,
            created_by=request.user,
            num_of_people=order.num_of_people,
            table_number=f"Virtual-{virtual_table.id}"
        )

        # Копируем выбранные продукты в новый заказ
        for item_id in selected_item_ids:
            item = get_object_or_404(OrderItem, id=item_id, order=order)
            quantity = item.quantity

            # Создаем новый OrderItem для нового заказа
            OrderItem.objects.create(
                order=new_order,
                product=item.product,
                quantity=quantity,
                discount_percentage=item.discount_percentage
            )

        messages.success(request, "Новый счет успешно создан.")
        return redirect('virtual_table_detail', virtual_table_id=virtual_table.id)
    else:
        order = get_object_or_404(Order, id=order_id)
        return render(request, 'split_order.html', {'order': order})

@login_required
@transaction.atomic
def virtual_table_detail(request, virtual_table_id):
    virtual_table = get_object_or_404(VirtualTable, id=virtual_table_id)
    order = get_object_or_404(Order, table_number=f"Virtual-{virtual_table_id}")

    if request.method == 'POST':
        # Удаление всех продуктов из виртуального стола и самого виртуального стола
        for item in order.order_items.all():
            item.delete()
        order.delete()
        virtual_table.delete()

        main_table = virtual_table.main_table
        main_order = main_table.get_active_order()

        #messages.success(request, "Счет успешно распечатан и виртуальный стол удален.")
        return redirect('cart_detail', order_id=main_order.id)

    total_price = sum(item.product.product_price * item.quantity for item in order.order_items.all())
    
    return render(request, 'virtual_table_detail.html', {
        'order': order,
        'total_price': total_price,
        'virtual_table': virtual_table,
    })
