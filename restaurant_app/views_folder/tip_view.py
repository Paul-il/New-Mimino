from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.core.exceptions import ValidationError
from django.shortcuts import render, redirect, get_object_or_404
from django.db import transaction
import logging

from ..models.tables import Tip, TipDistribution
from ..models.orders import Order

# Создайте объект логгера
logger = logging.getLogger(__name__)

@login_required
def tip_view(request):
    try:
        if request.method == 'POST':
            if 'tip' in request.POST:
                tip = request.POST.get('tip')
                table_id = request.POST.get('table_id')
                user_ids = request.POST.getlist('user_ids[]')

                order = get_object_or_404(Order, table_id=table_id, is_completed=False)

                # Проверка на наличие уже существующих чаевых для этого заказа
                if order.tips_provided():
                    raise ValidationError('Чаевые уже были добавлены успешно, можно спокойно закрывать стол.')

                tip_amount = float(tip)
                new_tip = Tip.objects.create(amount=tip_amount, order=order)

                if user_ids:  # Если какие-то идентификаторы пользователей были переданы
                    selected_users = [int(user_id) for user_id in user_ids]
                    if order.created_by.id not in selected_users:
                        selected_users.append(order.created_by.id)
                else:  # Если не было передано никаких идентификаторов пользователей
                    selected_users = [order.created_by.id]

                tip_per_user = tip_amount / len(selected_users)

                with transaction.atomic():
                    for user_id in selected_users:
                        user = User.objects.get(id=user_id)
                        
                        # Проверка на наличие уже существующей записи
                        existing_distribution = TipDistribution.objects.filter(tip=new_tip, user=user).first()
                        if existing_distribution:
                            raise ValidationError(f'Tips already provided for user {user.username}')
                        
                        TipDistribution.objects.create(tip=new_tip, user=user, amount=tip_per_user)
                        print(f"Distributed {tip_per_user} tips to user {user.username}")

                return redirect('rooms')
            else:
                all_users = User.objects.all()
                return render(request, 'order_detail.html', {'all_users': all_users})
    except ValidationError as e:
        return HttpResponse(str(e), status=400)
    else:
        return HttpResponse("Not Supported Method")

    
@login_required
def check_tips(request):
    if request.method == 'POST':
        table_id = request.POST.get('table_id')
        order = get_object_or_404(Order, table_id=table_id, is_completed=False)

        if order.tips_provided():  # использование нового метода
            return HttpResponse(status=200)  # чаевые были введены
        else:
            return HttpResponse("No tips provided", status=400)  # чаевые не были введены
    else:
        return HttpResponse("Not Supported Method", status=405)





