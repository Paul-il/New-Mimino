from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404
from restaurant_app.models.orders import Order, OrderItem, WaiterOrder
from django.http import HttpResponse, JsonResponse
from django.template.loader import render_to_string
from django.utils import timezone
from bs4 import BeautifulSoup
import cups
import tempfile
from django.conf import settings
import os
import shutil

def kitchen_template_view(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    context = {'order': order}
    html_content = render_to_string('kitchen_template.html', context)

    return HttpResponse(html_content)


def convert_html_to_text(cart_items):
    html = render_to_string('kitchen_template.html', {'cart_items': cart_items})
    soup = BeautifulSoup(html, 'html.parser')
    text = soup.get_text()
    return text


# Создайте папку для сохранения файлов заказов
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

    # Создаем или открываем файл, связанный с заказом
    order_file_path = os.path.join(settings.ORDERS_FILES_DIR, f'order_{order_id}.txt')

    # Создаем временный файл для новых продуктов
    with tempfile.NamedTemporaryFile(mode='w+', encoding='utf-8', delete=False) as temp_file:
        # Запишите заголовок во временный файл
        temp_file.write(title)
        temp_file.write(text_to_print)

        # Запишите комментарии во временный файл, если они есть
        if comments:
            temp_file.write('\n____________________________\nКомментарии:\n')
            temp_file.write(comments)

        temp_file_path = temp_file.name

    # Печатаем содержимое временного файла
    conn.printFile(printer_name, temp_file_path, title, options={})

    # Добавляем содержимое временного файла в основной файл заказа и удаляем временный файл
    with open(order_file_path, 'a', encoding='utf-8') as order_file:
        with open(temp_file_path, 'r', encoding='utf-8') as temp_file:
            shutil.copyfileobj(temp_file, order_file)
    os.unlink(temp_file_path)

    conn = cups.Connection()
    printers = conn.getPrinters()
    print(printers)


CATEGORY_SORT_ORDER = {
    "salads": 1,
}


def sort_items(item):
    return CATEGORY_SORT_ORDER.get(item.product.category, 999)


def get_sorted_cart_items(order):
    cart_items = OrderItem.objects.filter(order=order)
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

def print_items_for_printers(grouped_items, order_id, title, new_comments, order, print_items):
    for printer, items in grouped_items.items():
        text_to_print = ""
        for item in items:
            text_to_print += f"{item.product.product_name_rus}\t{item.quantity - item.printed_quantity}\n"
        
        comments_to_print = new_comments if new_comments != order.last_printed_comments else ''
        print_with_cups(order_id, title, text_to_print, comments_to_print, printer)

        if print_items:
            for item in items:
                item.printed_quantity = item.quantity
                item.save()


def update_order_comments(order, new_comments):
    order.comments = new_comments
    order.last_printed_comments = new_comments
    order.save()


def print_kitchen(request):
    try:
        order_id = request.GET.get('order_id')
        new_comments = request.GET.get('comments', '')
        order = get_object_or_404(Order, id=order_id)
        
        sorted_cart_items = get_sorted_cart_items(order)
        
        current_time = timezone.localtime().strftime('%H:%M')
        title = f"\n\n\nВремя печати: {current_time}\nСтол: {order.table.table_id}\nОфициант: {order.created_by.first_name}\n____________________________\n"
        
        grouped_items = group_items_by_printer(sorted_cart_items)
        
        print_items_str = request.GET.get('print_items', 'True')
        print_items = print_items_str.lower() == 'true'

        print_items_for_printers(grouped_items, order_id, title, new_comments, order, print_items)
        
        update_order_comments(order, new_comments)

        if grouped_items:
            return JsonResponse({'status': 'success', 'message': 'Заказ был успешно подтвержден.'})
        else:
            return JsonResponse({'status': 'warning', 'message': 'Нет новых товаров для печати.'})

    except ObjectDoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Заказ не найден.'})
    except cups.IPPError as e:
        return JsonResponse({'status': 'error', 'message': f"Ошибка при печати: {e}"})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': 'Произошла неизвестная ошибка.'})


def print_kitchen_for_waiter(request):
    try:
        print("КУШАТЬ")
        waiter_order_id = request.GET.get('waiter_order_id')
        new_comments = request.GET.get('comments', '')
        waiter_order = get_object_or_404(WaiterOrder, id=waiter_order_id)
        
        sorted_cart_items = get_sorted_cart_items(waiter_order)
        
        current_time = timezone.localtime().strftime('%H:%M')
        title = f"\n\n\nВремя печати: {current_time}\n(Для официанта): {waiter_order.created_by.first_name} \n____________________________\n"
        
        grouped_items = group_items_by_printer(sorted_cart_items)
        
        print_items_str = request.GET.get('print_items', 'True')
        print_items = print_items_str.lower() == 'true'

        print_items_for_printers(grouped_items, waiter_order_id, title, new_comments, waiter_order, print_items)
        
        update_order_comments(waiter_order, new_comments)

        # Удаление активного заказа после печати
        waiter_order.delete()

        if grouped_items:
            return JsonResponse({'status': 'success', 'message': 'Заказ был успешно подтвержден и отправлен на кухню.'})
        else:
            return JsonResponse({'status': 'warning', 'message': 'Нет новых товаров для печати.'})

    except ObjectDoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Заказ не найден.'})
    except cups.IPPError as e:
        return JsonResponse({'status': 'error', 'message': f"Ошибка при печати: {e}"})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': 'Произошла неизвестная ошибка.'})
