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
    if request.method != 'POST':
        return HttpResponse("Not Supported Method", status=405)

    try:
        if 'tip' not in request.POST:
            all_users = User.objects.all()
            return render(request, 'order_detail.html', {'all_users': all_users})

        tip = float(request.POST.get('tip'))
        table_id = request.POST.get('table_id')
        order = get_object_or_404(Order, table_id=table_id, is_completed=False)

        if order.tips_provided():
            raise ValidationError('Чаевые уже были добавлены успешно, можно спокойно закрывать стол.')

        new_tip = Tip.objects.create(amount=tip, order=order)

        user_ids = request.POST.getlist('user_ids[]', [])
        selected_users = [int(user_id) for user_id in user_ids]
        if order.created_by.id not in selected_users:
            selected_users.append(order.created_by.id)

        users = User.objects.filter(id__in=selected_users)
        tip_per_user = tip / len(users)

        with transaction.atomic():
            for user in users:
                existing_distribution = TipDistribution.objects.filter(tip=new_tip, user=user).first()
                if existing_distribution:
                    raise ValidationError(f'Tips already provided for user {user.username}')
                
                TipDistribution.objects.create(tip=new_tip, user=user, amount=tip_per_user)
                logger.info(f"Distributed {tip_per_user} tips to user {user.username}")

        return redirect('rooms')

    except ValidationError as e:
        logger.error(f"ValidationError: {str(e)}")
        return HttpResponse(str(e), status=400)

@login_required
def check_tips(request):
    if request.method != 'POST':
        return HttpResponse("Not Supported Method", status=405)

    table_id = request.POST.get('table_id')
    order = get_object_or_404(Order, table_id=table_id, is_completed=False)

    if order.tips_provided():
        return HttpResponse(status=200)  # чаевые были введены
    else:
        return HttpResponse("No tips provided", status=400)  # чаевые не были введены






