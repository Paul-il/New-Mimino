from django.template.loader import get_template
from weasyprint.fonts import FontConfiguration
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from datetime import datetime
from io import BytesIO
from weasyprint import HTML
import os
import traceback

from ..forms import DeliveryCustomerForm
from ..models import DeliveryOrder, DeliveryCustomer, Courier  # Добавьте импорт Courier


@login_required
def delivery_generate_pdf_view(request, delivery_phone_number, order_id):
    print("Starting delivery_generate_pdf_view...")
    try:
        # Get order data from database
        delivery_order = get_object_or_404(DeliveryOrder, pk=order_id, customer__delivery_phone_number=delivery_phone_number)
        delivery_customer = get_object_or_404(DeliveryCustomer, delivery_phone_number=delivery_phone_number)

        # Extract necessary data from models
        customer_name = delivery_customer.name
        delivery_city = delivery_customer.city
        delivery_street = delivery_customer.street
        delivery_floor = delivery_customer.floor
        delivery_house_number = delivery_customer.house_number
        delivery_apartment_number = delivery_customer.apartment_number
        delivery_intercom_code = delivery_customer.intercom_code

        # Get payment method and courier from request data
        payment_method = request.POST.get('payment_method')
        selected_courier = request.POST.get('courier')
        
         # Fetch the selected courier from the Courier model only if a courier is selected
        if selected_courier:
            try:
                courier_instance = Courier.objects.get(name=selected_courier)
                delivery_order.courier = courier_instance
            except Courier.DoesNotExist:
                print(f"Courier with name {selected_courier} not found in the database.")
        else:
            print("No courier selected.")

        # Update the order with the payment method and mark it as completed
        delivery_order.payment_method = payment_method
        delivery_order.is_completed = True
        delivery_order.save()
        
        # Get delivery form data from session
        delivery_customer_form = DeliveryCustomerForm()

        # Get all cart items in the order
        cart_items = []
        for cart in delivery_order.delivery_carts.all():
            for cart_item in cart.delivery_cart_items.all():
                cart_items.append(cart_item)
        print(f"Payment method set as: {payment_method}")
        
        # Calculate the total price of the order
        total_price = sum(item.quantity * item.product.product_price for item in cart_items)
        print(f"Total amount calculated: {total_price}")

        # Render the HTML template with the order data
        delivery_order.total_amount = total_price
        delivery_order.save()
        template = get_template('delivery_pdf_template.html')
        context = {
            'delivery_order': delivery_order,
            'cart_items': cart_items,
            'payment_method': payment_method,
            'total_price': total_price,
            'delivery_customer_form': delivery_customer_form,
            'delivery_phone_number': delivery_phone_number,
            'customer_name': customer_name,
            'city': delivery_city,
            'delivery_street': delivery_street,
            'delivery_floor': delivery_floor,
            'delivery_house_number': delivery_house_number,
            'delivery_apartment_number': delivery_apartment_number,
            'delivery_intercom_code': delivery_intercom_code,
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
        base_directory = os.path.join('pdfs', today, 'Delivery')  # Added 'Delivery' subdirectory
        os.makedirs(base_directory, exist_ok=True)

        if payment_method == 'מזומן':
            payment_directory = os.path.join(base_directory, 'cash')
        elif payment_method == 'כרטיס אשראי':
            payment_directory = os.path.join(base_directory, 'credit_card')
        else:
            payment_directory = os.path.join(base_directory, 'none')
        os.makedirs(payment_directory, exist_ok=True)

        filename = f'_Phone({delivery_phone_number})___{today}___{payment_method}__{total_price}.pdf'
        filepath = os.path.join(payment_directory, filename)
        
        with open(filepath, 'wb') as f:
            f.write(pdf_file.read())

        return redirect('ask_where')  # Redirecting to the desired location after processing

    except Exception as e:
        traceback.print_exc()
        error_message = f"An error occurred while generating the PDF: {str(e)}"
        return HttpResponse(error_message, content_type='text/plain', status=500)

"""    
@login_required
def set_courier(request, delivery_phone_number):
    print("Function set_courier started!")

    delivery_order = get_object_or_404(DeliveryOrder, customer__delivery_phone_number=delivery_phone_number)
    

    if request.method == "POST":
        courier_value = request.POST.get('courier')
        print("Starting set_courier...")  # Добавьте эту строку в начало функции

        if courier_value == "our_courier":
            delivery_order.courier = "Наш курьер"
        else:
            delivery_order.courier = "Соло"
        print(f"Courier set as: {courier_value}")
        delivery_order.is_completed = True
        delivery_order.save()

        return redirect('ask_where')
"""