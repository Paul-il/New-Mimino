from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm


from django.contrib import messages


@login_required
def personal_cabinet(request):
    return render(request, 'personal_cabinet.html')

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


