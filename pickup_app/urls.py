from django.urls import path


from pickup_app.pickup_views.pickup_menu_view import pickup_menu_view
from pickup_app.pickup_views.pickup_create_view import pickup_create_view
from pickup_app.pickup_views.pdf_template_view import pickup_pdf_template_view
from pickup_app.pickup_views.pickup_pdf_views import pickup_generate_pdf_view
from pickup_app.pickup_views.pickup_search_view import pickup_search_products_view
from pickup_app.pickup_views.pickup_kitchen_template_view import pickup_kitchen_view, print_kitchen

from pickup_app.pickup_views.pickup_cart_view import (
    pickup_cart_view, 
    pickup_add_to_cart_view, 
    pickup_remove_product_view,
    pickup_increase_product_view,
    pickup_decrease_product_view,
    pickup_total_price_view,
    pickup_empty_cart_view
                                          
)


app_name = 'pickup_app'

urlpatterns = [
    path('', pickup_create_view, name='pickup_create'),
    path('pickup_search/<str:phone_number>/', pickup_search_products_view, name='pickup_search_products'),

    path('pickup_empty_cart/<str:phone_number>/', pickup_empty_cart_view, name='pickup_empty_cart'),

    path('pickup_cart/<str:phone_number>/<str:category>/', pickup_cart_view, name='pickup_cart'),
    path('pickup_menu/<str:phone_number>/<str:category>/', pickup_menu_view, name='pickup_menu'),
    path('pickup_total_price/<str:phone_number>/', pickup_total_price_view, name='pickup_total_price'),
    path('pickup_add_to_cart/<str:phone_number>/<int:product_id>/<str:category>/', pickup_add_to_cart_view, name='pickup_add_to_cart'),

    path('pickup_kitchen_template/<str:phone_number>/<int:order_id>/', pickup_kitchen_view, name='pickup_kitchen_template'),

    path('print_kitchen/', print_kitchen, name='print_kitchen'),

    path('pickup_generate_pdf/<str:phone_number>/<int:order_id>/', pickup_generate_pdf_view, name='pickup_generate_pdf'),

    path('pickup_pdf_template/<str:phone_number>/<int:order_id>/', pickup_pdf_template_view, name='pickup_pdf_template'),

    path('pickup_remove_product/<str:phone_number>/<int:product_id>/', pickup_remove_product_view, name='pickup_remove_product'), 
    path('pickup_increase_product/<str:phone_number>/<int:product_id>/', pickup_increase_product_view, name='pickup_increase_product'),
    path('pickup_decrease_product/<str:phone_number>/<int:product_id>/', pickup_decrease_product_view, name='pickup_decrease_product'),
] 
