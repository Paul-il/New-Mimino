from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from restaurant_app.models.product import Product
from ..models import DeliveryCustomer, DeliveryOrder, DeliveryCart, DeliveryCartItem, Courier
from ..forms import ProductQuantityForm

CATEGORIES = {
    'salads': 'Салаты',
    'first_dishes': 'Закуски',
    'khachapuri': 'Хачапури',
    'bakery': 'Выпечка',
    'soups': 'Супы',
    'khinkali': 'Хинкали',
    'meat_dishes': 'Мясные блюда',
    'grill_meat': 'Мясо на огне',
    'garnish': 'Гарниры',
    'dessert': 'Десерты',
    'soft_drinks': 'Легкие напитки',
    'beer': 'Пиво',
    'wine' :'Вино',
    'vodka': 'Водка',
    'cognac': 'Коньяк',
    'whisky': 'Виски',
    'dessert_drinks': 'Горячие напитки',
    'mishloha':'Мишлоха',
}

def delivery_menu_view(request, delivery_phone_number, category, delivery_type):
    delivery_customer = get_object_or_404(DeliveryCustomer, delivery_phone_number=delivery_phone_number)
    delivery_order = DeliveryOrder.objects.filter(customer=delivery_customer, is_completed=False).first()
    
    # Фильтруем продукты, доступные для доставки
    products = Product.objects.filter(category=category, is_available_for_delivery=True).order_by('product_name_rus')
    product_quantity_form = ProductQuantityForm()

    context = {
        'delivery_phone_number': delivery_phone_number,
        'category': category,
        'products': products,
        'product_quantity_form': product_quantity_form,
        'CATEGORIES': CATEGORIES,
        'delivery_type': delivery_type,
    }

    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        courier = request.POST.get('courier')
        if courier:
            request.session['selected_courier'] = courier
            return redirect('delivery_app:delivery_menu', delivery_phone_number=delivery_phone_number, category=category, delivery_type=delivery_type)

        quantity = int(request.POST.get('quantity'))
        product = get_object_or_404(Product, id=product_id)

        cart, created = DeliveryCart.objects.get_or_create(delivery_order=delivery_order, customer=delivery_customer)
        cart_item, created = DeliveryCartItem.objects.get_or_create(cart=cart, product=product)

        if not created:
            cart_item.quantity += quantity
        else:
            cart_item.quantity = quantity
        cart_item.save()
        
        return redirect('delivery_app:delivery_cart', delivery_phone_number=delivery_phone_number, delivery_type=delivery_type)

    return render(request, 'delivery_menu.html', context)

def set_courier(request, delivery_phone_number):
    if request.method == 'POST':
        selected_courier_name = request.POST.get('courier')

        # Получаем заказ по номеру телефона
        delivery_customer = DeliveryCustomer.objects.get(delivery_phone_number=delivery_phone_number)
        delivery_order = DeliveryOrder.objects.get(customer=delivery_customer, is_completed=False)

        # Находим курьера по имени
        try:
            selected_courier = Courier.objects.get(name=selected_courier_name)
        except Courier.DoesNotExist:
            # здесь можно добавить сообщение об ошибке для пользователя
            return render(request, 'error_page.html', {'message': 'Курьер не найден!'})


        # Устанавливаем курьера для заказа и сохраняем заказ
        delivery_order.courier = selected_courier
        delivery_order.save()
        
    return redirect('delivery_app:delivery_menu', delivery_phone_number=delivery_phone_number, category='delivery')
