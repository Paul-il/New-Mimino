from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from delivery_app.models import DeliveryOrder, DeliveryCart, DeliveryCartItem
from django.template.loader import render_to_string
from django.utils import timezone
from bs4 import BeautifulSoup

def remove_empty_lines_and_spaces(text):
    lines = text.split('\n')
    cleaned_lines = [line.strip() for line in lines if line.strip()]
    cleaned_text = '\n'.join(cleaned_lines)
    return cleaned_text

def convert_html_to_text(cart_items):
    html = render_to_string('delivery_kitchen_template.html', {'cart_items': cart_items})
    soup = BeautifulSoup(html, 'html.parser')
    text = soup.get_text()
    return text

def delivery_kitchen_view(request, phone_number, order_id):
    order = get_object_or_404(DeliveryOrder, delivery_phone=phone_number, id=order_id)
    cart_items = DeliveryCart.objects.filter(cart__delivery_order=order)

    context = {'order': order, 'cart_items': cart_items, }
    return render(request, 'delivery_kitchen_template.html', context)

import cups
import tempfile
import os

def print_with_cups(text_to_print, printer_name):
    conn = cups.Connection()
    printers = conn.getPrinters()

    if printer_name not in printers:
        printer_name = list(printers.keys())[0]  # если выбранный принтер не найден, используем первый доступный

    # Сохраняем текст во временный файл
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_file.write(text_to_print.encode('utf-8'))
        temp_file_path = temp_file.name

    # Печатаем содержимое временного файла
    conn.printFile(printer_name, temp_file_path, title="Printing from Django", options={})
    
    # Удаляем временный файл
    os.unlink(temp_file_path)

def sort_items(item):
    if item.product.category == "salads":
        return 0
    else:
        return 1

def print_kitchen(request):
    phone_number = request.GET.get('phone_number')
    order_id = request.GET.get('order_id')
    order = get_object_or_404(DeliveryOrder, customer__delivery_phone_number=phone_number, id=order_id)
    cart_items = DeliveryCartItem.objects.filter(delivery_order=order)
    sorted_cart_items = sorted(cart_items, key=sort_items)

    # Группируем продукты по принтерам
    grouped_items = {}
    for item in sorted_cart_items:
        new_quantity = item.quantity - item.printed_quantity
        if new_quantity <= 0:
            continue
        printer = item.product.printer
        if printer not in grouped_items:
            grouped_items[printer] = []
        grouped_items[printer].append(item)

    new_items_found = False
    for printer, items in grouped_items.items():
        current_time = timezone.localtime().strftime('%H:%M')
        text_to_print = f"\n\n\nВремя печати: {current_time}\nНа Вынос\n____________________________\n"
        for item in items:
            text_to_print += f"{item.product.product_name_rus}\t{item.quantity - item.printed_quantity}\n"
        
        # Отправляем текст на печать
        print_with_cups(text_to_print, printer_name=printer)
        new_items_found = True

        # Обновляем количество напечатанных товаров
        for item in items:
            item.printed_quantity = item.quantity
            item.save()

    if new_items_found:
        return JsonResponse({'status': 'success', 'message': 'Заказ был отправлен на кухню.'})
    else:
        return JsonResponse({'status': 'warning', 'message': 'Нет новых товаров для печати.'})







