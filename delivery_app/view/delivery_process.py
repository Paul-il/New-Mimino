from django.shortcuts import render, redirect

# Допустим, вы используете декоратор login_required
from django.contrib.auth.decorators import login_required

@login_required
def delivery_process_view(request, delivery_type):
    # Ваша логика обработки в зависимости от delivery_type
    if delivery_type in ['now', 'later']:
        # Перенаправление на страницу проверки номера телефона с параметром delivery_type
        return redirect('delivery_app:check_delivery_number', delivery_type=delivery_type)
    else:
        # Обработка некорректного типа доставки
        return render(request, 'error_page.html', {'error_message': 'Неверный тип доставки'})

