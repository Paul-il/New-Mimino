import os
from weasyprint.fonts import FontConfiguration
from weasyprint import HTML
from datetime import datetime
from io import BytesIO
from django.http import JsonResponse
from django.template.loader import get_template
from django.http import HttpResponse
from django.shortcuts import render

from restaurant_app.models.orders import Order

def generate_pdf_view(request, order_id):
    try:
        # Get order data from database
        order = Order.objects.get(id=order_id)
        print(order)
        # Get payment method from request data
        payment_method = request.POST.get('payment_method')
        
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
        today = datetime.now().strftime('%Y-%m-%d')
        directory = os.path.join('pdfs', today)
        if payment_method == 'מזומן':
            cash_directory = os.path.join(directory, 'cash')
            os.makedirs(cash_directory, exist_ok=True)
            filename = f'_TableNumber({table_number})___{today}___{payment_method}.pdf'
            filepath = os.path.join(cash_directory, filename)
            order.delete()
            
        elif payment_method == 'כרטיס אשראי':
            cc_directory = os.path.join(directory, 'credit_card')
            os.makedirs(cc_directory, exist_ok=True)
            filename = f'_TableNumber({table_number})___{today}___{payment_method}.pdf'
            filepath = os.path.join(cc_directory, filename)
            order.delete()
        else:
            none_directory = os.path.join(directory, 'none')
            os.makedirs(none_directory, exist_ok=True)
            filename = f'_TableNumber({table_number})___{today}___{payment_method}.pdf'
            filepath = os.path.join(none_directory, filename)
            

        with open(filepath, 'wb') as f:
            f.write(pdf_file.read())

        
        return JsonResponse({'thank': "You."})
    
    except Exception as e:
        error_message = f"An error occurred while generating the PDF: {str(e)}"
        return HttpResponse(error_message, content_type='text/plain', status=500)
