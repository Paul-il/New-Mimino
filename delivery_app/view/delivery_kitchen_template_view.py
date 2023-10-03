from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from delivery_app.models import DeliveryOrder, DeliveryCart, DeliveryCartItem
from django.template.loader import render_to_string
from django.utils import timezone
from bs4 import BeautifulSoup

import cups
import tempfile
import os

TIME_FORMAT = '%H:%M'

def remove_empty_lines_and_spaces(text):
    return '\n'.join([line.strip() for line in text.split('\n') if line.strip()])


def convert_html_to_text(cart_items):
    html = render_to_string('delivery_kitchen_template.html', {'cart_items': cart_items})
    return BeautifulSoup(html, 'html.parser').get_text()


def delivery_kitchen_view(request, phone_number, order_id):
    order = get_object_or_404(DeliveryOrder, delivery_phone=phone_number, id=order_id)
    cart_items = DeliveryCart.objects.filter(cart__delivery_order=order)
    return render(request, 'delivery_kitchen_template.html', {'order': order, 'cart_items': cart_items})


def print_with_cups(text_to_print, printer_name):
    conn = cups.Connection()
    printers = conn.getPrinters()
    printer_name = printers.get(printer_name) or list(printers.keys())[0]
    
    with tempfile.NamedTemporaryFile(delete=False, mode='w') as temp_file:
        temp_file.write(text_to_print)
        temp_file_path = temp_file.name

    conn.printFile(printer_name, temp_file_path, title="Printing from Django", options={})
    os.unlink(temp_file_path)


def sort_items(item):
    return 0 if item.product.category == "salads" else 1


def group_items_by_printer(sorted_cart_items):
    return {item.product.printer: item for item in sorted_cart_items if item.quantity - item.printed_quantity > 0}


def print_kitchen(request):
    phone_number = request.GET.get('phone_number')
    order_id = request.GET.get('order_id')

    if not phone_number or not order_id:
        return JsonResponse({'status': 'error', 'message': 'Необходимые параметры отсутствуют.'})

    try:
        order = get_object_or_404(DeliveryOrder, customer__delivery_phone_number=phone_number, id=order_id)
        cart_items = DeliveryCartItem.objects.filter(delivery_order=order)
        grouped_items = group_items_by_printer(sorted(cart_items, key=sort_items))

        items_to_update = []
        new_items_found = False
        for printer, items in grouped_items.items():
            text_to_print = f"\n\n\nВремя печати: {timezone.localtime().strftime(TIME_FORMAT)}\nНа Вынос\n____________________________\n"
            text_to_print += '\n'.join([f"{item.product.product_name_rus}\t{item.quantity - item.printed_quantity}" for item in items])

            print_with_cups(text_to_print, printer_name=printer)
            items_to_update.extend(items)
            new_items_found = True

        if items_to_update:
            DeliveryCartItem.objects.bulk_update(items_to_update, ['printed_quantity'])

        return JsonResponse({'status': 'success' if new_items_found else 'warning', 'message': 'Заказ был отправлен на кухню.' if new_items_found else 'Нет новых товаров для печати.'})

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': f'Произошла ошибка: {str(e)}.'})

