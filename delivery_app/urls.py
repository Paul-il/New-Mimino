from django.urls import path
from .view.clear_solo_dept import clear_solo_debt
from .view.delivery_views import delivery_view
from .view.delivery_summary import delivery_summary
from .view.delivery_menu_views import delivery_menu_view, set_courier
from .view.delivery_kitchen_template_view import print_kitchen
from .view.delivery_search_view import delivery_search_view
from .view.delivery_pdf_views import delivery_generate_pdf_view
from .view.delivery_template_pdf import delivery_pdf_template_view
from .view.add_delivery_customer_views import add_delivery_customer_view, save_delivery_customer_changes_view
from .view.check_delivery_customer_views import check_delivery_customer_view

from .view.delivery_cart_views import (
    delivery_add_to_cart_view, 
    delivery_cart_view,
    delivery_increase_product_view,
    delivery_decrease_product_view,
    delivery_remove_product_view,
    delivery_empty_cart_view,
     )

app_name = 'delivery_app'


urlpatterns = [
    path('check_delivery_number', delivery_view, name='check_delivery_number'),
    path('add_delivery_customer/<str:delivery_phone_number>/', add_delivery_customer_view, name='add_delivery_customer'),
    path('save_delivery_customer_changes/<str:delivery_phone_number>/', save_delivery_customer_changes_view, name='save_delivery_customer_changes'),
    path('check_delivery_customer/<str:delivery_phone_number>/', check_delivery_customer_view, name='check_delivery_customer'),
    path('delivery_add_to_cart/<str:delivery_phone_number>/<str:category>/', delivery_add_to_cart_view, name='delivery_add_to_cart'),
    path('delivery_menu/<str:delivery_phone_number>/<str:category>/', delivery_menu_view, name='delivery_menu'),

    path('delivery_pdf_template/<str:phone_number>/<int:order_id>/', delivery_pdf_template_view, name='delivery_pdf_template'),

    path('print_kitchen/', print_kitchen, name='print_kitchen'),

    path('delivery_search/<str:delivery_phone_number>/', delivery_search_view, name='delivery_search_products'),

    path('delivery_empty_cart/<str:delivery_phone_number>/', delivery_empty_cart_view, name='delivery_empty_cart' ),

    path('cart/<str:delivery_phone_number>/', delivery_cart_view, name='delivery_cart'),
    path('cart/<str:delivery_phone_number>/increase/<int:product_id>/', delivery_increase_product_view, name='delivery_increase_product'),
    path('cart/<str:delivery_phone_number>/decrease/<int:product_id>/', delivery_decrease_product_view, name='delivery_decrease_product'),
    path('cart/<str:delivery_phone_number>/remove/<int:product_id>/', delivery_remove_product_view, name='delivery_remove_product'),
    path('cart/<str:delivery_phone_number>/<int:order_id>/pdf/', delivery_generate_pdf_view, name='delivery_generate_pdf'),
    path('set_courier/<str:delivery_phone_number>/', set_courier, name='set_courier'),
    path('clear_solo_debt/', clear_solo_debt, name='clear_solo_debt'),
    path('delivery_summary/', delivery_summary, name='delivery_summary'),


]
