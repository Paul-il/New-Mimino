from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

@login_required
def ask_where_view(request):
    if request.user.is_authenticated:
        return render(request, 'ask_where.html')
    else:
        return redirect('login')