from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User, Group
from django.contrib import messages
from datetime import timedelta
from django.utils import timezone

from ..models.tables import Table
from ..models.orders import Order

@login_required
def personal_cabinet(request):
    waiters = User.objects.filter(groups__name='Waiters')
    tables = Table.objects.all()
    context = {
        'waiters': waiters,
        'tables': tables,
    }
    return render(request, 'personal_cabinet.html', context)

@login_required
def select_table(request):
    if request.method == 'POST':
        table_id = request.POST.get('table_id')
        return redirect('select_waiter', table_id=table_id)
    
    # Получаем только столы с активными заказами, содержащими продукты
    tables = Table.objects.filter(is_available=True, orders__is_completed=False, orders__order_items__isnull=False).distinct()
    context = {
        'tables': tables,
    }
    return render(request, 'select_table.html', context)

@login_required
def select_waiter(request, table_id):
    four_weeks_ago = timezone.now() - timedelta(weeks=4)
    
    # Получаем пользователя, который открыл этот стол (если он есть)
    opener = Order.objects.filter(table_id=table_id).values_list('created_by', flat=True).first()
    
    # Получаем всех пользователей, которые были активны хотя бы 4 недели назад и исключаем открывателя, если он есть
    if opener:
        waiters = User.objects.filter(last_login__gte=four_weeks_ago).exclude(id=opener)
    else:
        waiters = User.objects.filter(last_login__gte=four_weeks_ago)

    context = {
        'waiters': waiters,
        'table_id': table_id,
        'active_users': User.objects.filter(last_login__gte=four_weeks_ago),  # добавляем для отладки
        'opener': opener  # добавляем для отладки
    }
    return render(request, 'select_waiter.html', context)


@login_required
def transfer_order(request):
    if request.method == 'POST':
        new_waiter_id = request.POST.get('new_waiter')
        table_id = request.POST.get('table_id')

        new_waiter = get_object_or_404(User, id=new_waiter_id)
        table = get_object_or_404(Table, id=table_id)

        # Перенос всех активных заказов
        orders = Order.objects.filter(table=table, is_completed=False)
        for order in orders:
            order.created_by = new_waiter
            order.save()

        messages.success(request, 'Заказ успешно перенесен.')
        return redirect('rooms')  # Перенаправление на страницу rooms.html

    return redirect('personal_cabinet')

@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Сохраняем сессию пользователя
            messages.success(request, 'Ваш пароль был успешно изменен!')
            return redirect('personal_cabinet')
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки ниже.')
    else:
        form = PasswordChangeForm(request.user)
        form.fields['old_password'].label = 'Старый пароль'
        form.fields['new_password1'].label = 'Новый пароль'
        form.fields['new_password2'].label = 'Подтверждение нового пароля'
        
        # Заменяем сообщения об ошибках на русском языке
        form.error_messages['password_mismatch'] = 'Введенные пароли не совпадают.'
        form.fields['new_password1'].error_messages = {
            'password_too_similar': 'Ваш пароль не должен быть слишком похож на другую вашу личную информацию.',
            'password_too_short': 'Ваш пароль должен содержать не менее 8 символов.',
            'password_too_common': 'Ваш пароль не должен быть распространённым паролем.',
            'password_entirely_numeric': 'Ваш пароль не должен состоять только из цифр.'
        }

    return render(request, 'change_password.html', {'form': form})

@login_required
def edit_profile(request):
    if request.method == 'POST':
        user = request.user
        user.first_name = request.POST['first_name']
        user.last_name = request.POST['last_name']
        user.email = request.POST['email']
        user.save()
        messages.success(request, 'Ваш профиль был успешно обновлен!')
        return redirect('personal_cabinet')
    return render(request, 'edit_profile.html', {'user': request.user})



