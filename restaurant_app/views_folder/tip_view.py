from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.db import transaction
from ..models.tables import Tip, TipDistribution
from ..models.orders import Order
from django.utils import timezone

import logging

logger = logging.getLogger(__name__)

from django.http import JsonResponse

from django.http import JsonResponse

@login_required
def tip_view(request, table_id):
    if request.method == 'POST':
        with transaction.atomic():
            try:
                tip_amount = float(request.POST.get('tip'))
                order = get_object_or_404(Order, table__id=table_id, is_completed=False)

                if order.tips_provided():
                    raise ValueError('Чаевые уже были добавлены.')

                print(f"Добавление чаевых: {tip_amount} к заказу {order.id} на столе {table_id}. Время: {timezone.now()}")

                new_tip = Tip.objects.create(amount=tip_amount, order=order)

                user_ids = request.POST.getlist('user_ids[]')

                if str(order.created_by.id) not in user_ids:
                    user_ids.append(str(order.created_by.id))

                print(f"Список ID официантов для распределения чаевых: {user_ids}")

                amount_per_user = tip_amount / len(user_ids)
                print(f"Каждому официанту распределяется: {amount_per_user}")

                distributed_tips = []

                for user_id in user_ids:
                    user = User.objects.get(id=user_id)
                    TipDistribution.objects.create(tip=new_tip, user=user, amount=amount_per_user)
                    distributed_tips.append({'first_name': user.first_name, 'amount': amount_per_user})

                order.is_completed = True
                order.save()

                print("Статус заказа обновлен на 'завершен'.")
                for tip in distributed_tips:
                    print(f"{tip['first_name']} получает {tip['amount']} чаевых.")

                return JsonResponse({
                    'message': 'Чаевые успешно добавлены.',
                    'distributed_tips': distributed_tips,
                    'redirect_url': '/rooms/'
                })

            except Exception as e:
                print(f"Ошибка при распределении чаевых: {e}")
                return JsonResponse({'error': str(e)}, status=400)
    else:
        all_users = User.objects.filter(is_active=True).only('id', 'username')
        return render(request, 'tip.html', {'all_users': all_users, 'table_id': table_id})

@login_required
def check_tips(request):
    if request.method != 'POST':
        return HttpResponse("Not Supported Method", status=405)

    table_id = request.POST.get('table_id')
    order = get_object_or_404(Order, table__id=table_id, is_completed=False)

    if order.tips_provided():
        return HttpResponse(status=200)  # Чаевые были введены
    else:
        return HttpResponse("No tips provided", status=400)  # Чаевые не были введены
