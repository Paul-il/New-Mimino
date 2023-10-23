from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

def login_page_view(request):
    context = {}  # Создаем словарь контекста для передачи данных в шаблон

    if request.method == 'POST':
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            return redirect('ask_where')
        else:
            context['error'] = 'Invalid login credentials'  # Добавляем сообщение об ошибке в контекст

    return render(request, 'index.html', context)

@login_required
def logout_view(request):
    logout(request)
    return redirect('login')
