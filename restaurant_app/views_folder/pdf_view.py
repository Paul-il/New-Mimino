import os
import requests
import json
from weasyprint.fonts import FontConfiguration
from weasyprint import HTML
from django.utils import timezone  # Импорт timezone из django.utils
from io import BytesIO
from django.http import JsonResponse
from django.template.loader import get_template
from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from restaurant_app.models.orders import Order

from django.shortcuts import redirect

def generate_pdf_view(request, order_id):
    try:
        # Get order data from database
        order = Order.objects.get(id=order_id)
        print(order)

        # Get payment method from request data
        payment_method = request.POST.get('payment_method')

        # Get split payment amounts from request data
        cash_amount = request.POST.get('cash_amount')
        card_amount = request.POST.get('card_amount')

        # Calculate the total price of the order
        total_price = sum(
            order_item.quantity * order_item.product.product_price
            for order_item in order.order_items.all()
        )

        # Render the HTML template with the order data
        template = get_template('pdf_template.html')
        html = template.render({'order': order, 'payment_method': payment_method, 'total_price': total_price})
        font_config = FontConfiguration()

        # Convert the HTML to a PDF using weasyprint
        pdf_file = BytesIO()
        HTML(string=html, base_url=request.build_absolute_uri()).write_pdf(
            pdf_file,
            font_config=font_config,
        )
        pdf_file.seek(0)

        # Save the PDF to a file with a unique filename
        table_number = order.table.table_id
        today = timezone.localtime(timezone.now()).strftime('%Y-%m-%d')
        directory = os.path.join('pdfs', today)

        filename = f'_TableNumber({table_number})___{today}___{payment_method}__{total_price}.pdf'

        if payment_method == 'מזומן':
            cash_directory = os.path.join(directory, 'cash')
            os.makedirs(cash_directory, exist_ok=True)
            filepath = os.path.join(cash_directory, filename)
            order.is_completed = True
            order.payment_method = 'Cash'
            order.cash_amount = cash_amount
            order.save()
            
        elif payment_method == 'כרטיס אשראי':
            cc_directory = os.path.join(directory, 'credit_card')
            os.makedirs(cc_directory, exist_ok=True)
            filepath = os.path.join(cc_directory, filename)
            order.is_completed = True
            order.payment_method = 'Credit Card'
            order.card_amount = card_amount
            order.save()
        else:
            none_directory = os.path.join(directory, 'none')
            os.makedirs(none_directory, exist_ok=True)
            filepath = os.path.join(none_directory, filename)
            order.payment_method = 'None'
            order.save()

        with open(filepath, 'wb') as f:
            f.write(pdf_file.read())

        return redirect('rooms')
    
    except Exception as e:
        error_message = f"An error occurred while generating the PDF: {str(e)}"
        return HttpResponse(error_message, content_type='text/plain', status=500)




