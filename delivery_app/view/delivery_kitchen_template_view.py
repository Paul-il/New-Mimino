from django.shortcuts import get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from delivery_app.models import DeliveryOrder, DeliveryCartItem
from django.http import HttpResponse, JsonResponse
from django.template.loader import render_to_string
from django.utils import timezone
from bs4 import BeautifulSoup
import sys

if sys.platform != "win32":  # Проверяем, что ОС не Windows
    import cups
    
import tempfile
from django.conf import settings
import os
import shutil

def convert_html_to_text(cart_items):
    html = render_to_string('delivery_kitchen_template.html', {'cart_items': cart_items})
    soup = BeautifulSoup(html, 'html.parser')
    text = soup.get_text()
    return text

ORDERS_FILES_DIR = os.path.join(settings.MEDIA_ROOT, 'orders_files')
if not os.path.exists(ORDERS_FILES_DIR):
    os.makedirs(ORDERS_FILES_DIR)

def ensure_orders_files_dir_exists():
    if not os.path.exists(ORDERS_FILES_DIR):
        os.makedirs(ORDERS_FILES_DIR)

def print_with_cups(order_id, title, text_to_print, comments, printer_name):
    ensure_orders_files_dir_exists()
    conn = cups.Connection()
    printers = conn.getPrinters()
    if printer_name not in printers:
        printer_name = list(printers.keys())[0]
    order_file_path = os.path.join(ORDERS_FILES_DIR, f'order_{order_id}.txt')
    with tempfile.NamedTemporaryFile(mode='w+', encoding='utf-8', delete=False) as temp_file:
        temp_file.write(title)
        temp_file.write(text_to_print)
        if comments:
            temp_file.write('\n____________________________\nКомментарии:\n')
            temp_file.write(comments)
        temp_file_path = temp_file.name
    conn.printFile(printer_name, temp_file_path, title, options={})
    with open(order_file_path, 'a', encoding='utf-8') as order_file:
        with open(temp_file_path, 'r', encoding='utf-8') as temp_file:
            shutil.copyfileobj(temp_file, order_file)
    os.unlink(temp_file_path)

CATEGORY_SORT_ORDER = {
    "salads": 1,
}

def sort_items(item):
    return CATEGORY_SORT_ORDER.get(item.product.category, 999)

def get_sorted_delivery_cart_items(order):
    cart_items = DeliveryCartItem.objects.filter(delivery_order=order)
    return sorted(cart_items, key=sort_items)

def group_items_by_printer(sorted_cart_items):
    grouped_items = {}
    for item in sorted_cart_items:
        new_quantity = item.quantity - item.printed_quantity
        if new_quantity <= 0:
            continue
        printer = item.product.printer
        if printer not in grouped_items:
            grouped_items[printer] = []
        grouped_items[printer].append(item)
    return grouped_items

def print_delivery_items_for_printers(grouped_items, order_id, title, new_comments, order, print_items):
    for printer, items in grouped_items.items():
        text_to_print = ""
        for item in items:
            text_to_print += f"{item.product.product_name_rus}\t{item.quantity - item.printed_quantity}\n"
        comments_to_print = new_comments
        print_with_cups(order_id, title, text_to_print, comments_to_print, printer)
        if print_items:
            for item in items:
                item.printed_quantity = item.quantity
                item.save()

def delivery_kitchen_template_view(request, phone_number, order_id):
    order = get_object_or_404(DeliveryOrder, customer__delivery_phone_number=phone_number, id=order_id)
    context = {'order': order}
    html_content = render_to_string('delivery_kitchen_template.html', context)
    return HttpResponse(html_content)

def print_kitchen(request):
    try:
        phone_number = request.GET.get('phone_number')
        order_id = request.GET.get('order_id')
        new_comments = request.GET.get('comments', '')
        order = get_object_or_404(DeliveryOrder, customer__delivery_phone_number=phone_number, id=order_id)
        sorted_cart_items = get_sorted_delivery_cart_items(order)
        current_time = timezone.localtime().strftime('%H:%M')
        title = f"\n\n\nВремя печати: {current_time}\nДоставка\n____________________________\n"
        grouped_items = group_items_by_printer(sorted_cart_items)
        print_items_str = request.GET.get('print_items', 'True')
        print_items = print_items_str.lower() == 'true'
        print_delivery_items_for_printers(grouped_items, order_id, title, new_comments, order, print_items)
        if grouped_items:
            return JsonResponse({'status': 'success', 'message': 'Заказ был успешно подтвержден.'})
        else:
            return JsonResponse({'status': 'warning', 'message': 'Нет новых товаров для печати.'})
    except ObjectDoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Заказ не найден.'})
    except cups.IPPError as e:
        return JsonResponse({'status': 'error', 'message': f"Ошибка при печати: {e}"})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': f'Произошла неизвестная ошибка: {e}'})

