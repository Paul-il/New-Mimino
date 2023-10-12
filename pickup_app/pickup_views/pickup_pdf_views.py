from django.template.loader import get_template
from weasyprint.fonts import FontConfiguration
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from datetime import datetime
from io import BytesIO
from weasyprint import HTML
import os
import traceback
from ..models import PickupOrder, Cart

@login_required
def pickup_generate_pdf_view(request, phone_number, order_id):
    try:
        # Get order data from database
        order = get_object_or_404(PickupOrder, phone=phone_number)

        # Get payment method from request data
        payment_method = request.POST.get('payment_method')
        pay_button_value = request.POST.get('pay-button')

        # Get all cart items in the order
        cart_items = []
        for cart in order.carts.all():
            for item in cart.cart_items.all():
                cart_items.append(item)

        # Calculate the total price of the order
        total_price = sum(item.quantity * item.product.product_price for item in cart_items)

        # Render the HTML template with the order data
        template = get_template('pickup_pdf_template.html')
        context = {
            'order': order,
            'cart_items': cart_items,
            'payment_method': payment_method,
            'total_price': total_price,
        }
        html = template.render(context)
        font_config = FontConfiguration()

        # Convert the HTML to a PDF using weasyprint
        pdf_file = BytesIO()
        HTML(string=html, base_url=request.build_absolute_uri()).write_pdf(
            pdf_file,
            font_config=font_config,
        )
        pdf_file.seek(0)

        # Save the PDF to a file with a unique filename
        today = datetime.now().strftime('%Y-%m-%d')
        base_directory = os.path.join('pdfs', today, 'Pickup')
        os.makedirs(base_directory, exist_ok=True)

        if payment_method == 'מזומן':
            payment_directory = os.path.join(base_directory, 'cash')
        elif payment_method == 'כרטיס אשראי':
            payment_directory = os.path.join(base_directory, 'credit_card')
        else:
            payment_directory = os.path.join(base_directory, 'none')
        os.makedirs(payment_directory, exist_ok=True)

        filename = f'_Phone:({phone_number})___{today}___{payment_method}__{total_price}.pdf'
        filepath = os.path.join(payment_directory, filename)
        
        with open(filepath, 'wb') as f:
            f.write(pdf_file.read())

        # Check if the bill was paid
        if pay_button_value:
            # Update the order
            order.total_amount = total_price
            order.is_completed = True
            order.status = 'completed'
            order.save()

            # Clear the cart
            cart = Cart.objects.get(pickup_order=order)
            cart.cart_items.all().delete()

            # Redirect to the desired page
            return redirect(reverse('ask_where'))
        else:
            return JsonResponse({'message': "PDF успешно создан!"})

    except Exception as e:
        traceback.print_exc()
        error_message = f"Произошла ошибка при создании PDF или обработке заказа: {str(e)}"
        return HttpResponse(error_message, content_type='text/plain', status=500)
