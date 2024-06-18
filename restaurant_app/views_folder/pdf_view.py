from decimal import Decimal
from django.shortcuts import get_object_or_404, redirect, HttpResponse
from ..models.orders import Order
from django.conf import settings

def generate_pdf_view(request, order_id):
    if request.method == 'POST':
        try:
            order = get_object_or_404(Order, id=order_id)

            payment_method = request.POST.get('payment_method')
            cash_amount = request.POST.get('cash_amount')
            card_amount = request.POST.get('card_amount')

            if payment_method == 'cash':
                order.payment_method = 'cash'
                order.cash_amount = Decimal(cash_amount) if cash_amount else None
                order.card_amount = None
            elif payment_method == 'card':
                order.payment_method = 'card'
                order.card_amount = Decimal(card_amount) if card_amount else None
                order.cash_amount = None
            elif cash_amount and card_amount:
                order.payment_method = 'mixed'
                order.cash_amount = Decimal(cash_amount) if cash_amount else None
                order.card_amount = Decimal(card_amount) if card_amount else None
            else:
                order.payment_method = None
                order.cash_amount = None
                order.card_amount = None

            order.status = Order.Status.COMPLETED
            order.is_completed = True
            order.payment_processed = True
            order.save()

            return redirect('rooms')

        except Exception as e:
            error_message = f"An error occurred: {str(e)}"
            return HttpResponse(error_message, content_type='text/plain', status=500)