from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404
from django.db import transaction
from django.utils import timezone
from ..models.tables import Tip, TipDistribution
from ..models.orders import Order

import logging

logger = logging.getLogger(__name__)

@login_required
def tip_view(request, table_id):
    if request.method == 'POST':
        with transaction.atomic():
            try:
                tip_amount = float(request.POST.get('tip'))
                order = Order.objects.filter(table__id=table_id, is_completed=True, payment_processed=True).order_by('-updated_at').first()

                if not order:
                    raise ValueError('No matching order found or order is not completed/payment not processed.')

                if Tip.objects.filter(order=order).exists():
                    raise ValueError('Чаевые уже были добавлены.')

                logger.info(f"Adding tip: {tip_amount} to order {order.id} at table {table_id}. Time: {timezone.now()}")

                new_tip = Tip.objects.create(amount=tip_amount, order=order)

                user_ids = request.POST.getlist('user_ids[]')

                if str(order.created_by.id) not in user_ids:
                    user_ids.append(str(order.created_by.id))

                logger.info(f"List of waiter IDs for tip distribution: {user_ids}")

                amount_per_user = tip_amount / len(user_ids)
                logger.info(f"Amount distributed to each waiter: {amount_per_user}")

                distributed_tips = []

                for user_id in user_ids:
                    user = get_object_or_404(User, id=user_id)
                    TipDistribution.objects.create(tip=new_tip, user=user, amount=amount_per_user)
                    distributed_tips.append({'first_name': user.first_name, 'amount': amount_per_user})

                logger.info("Order status remains 'completed' after adding tips.")
                for tip in distributed_tips:
                    logger.info(f"{tip['first_name']} receives {tip['amount']} in tips.")

                return JsonResponse({
                    'message': 'Чаевые успешно добавлены.',
                    'distributed_tips': distributed_tips,
                    'redirect_url': '/rooms/'
                })

            except Exception as e:
                logger.error(f"Error distributing tips: {e}")
                return JsonResponse({'error': str(e)}, status=400)
    else:
        all_users = User.objects.filter(is_active=True).only('id', 'username')
        return render(request, 'tip.html', {'all_users': all_users, 'table_id': table_id})

@login_required
def check_tips(request):
    if request.method != 'POST':
        return HttpResponse("Not Supported Method", status=405)

    table_id = request.POST.get('table_id')
    order = Order.objects.filter(table__id=table_id, is_completed=True, payment_processed=True).order_by('-updated_at').first()

    if not order:
        return HttpResponse("Order not found or not completed", status=404)

    if Tip.objects.filter(order=order).exists():
        return HttpResponse(status=200)  # Чаевые были введены
    else:
        return HttpResponse("No tips provided", status=400)  # Чаевые не были введены