from django.urls import path
from .view.clear_solo_dept import clear_solo_debt
from .view.delivery_views import delivery_view
from .view.delivery_process import delivery_process_view
from .view.delivery_summary import delivery_summary, stas_summary
from .view.delivery_template_pdf import delivery_pdf_template_view
from .view.delivery_menu_views import delivery_menu_view, set_courier
from .view.delivery_kitchen_template_view import delivery_print_kitchen
from .view.delivery_search_view import delivery_search_view
from .view.delivery_close_cart import delivery_close_cart_view
from .view.add_delivery_customer_views import add_delivery_customer_view, save_delivery_customer_changes_view
from .view.check_delivery_customer_views import check_delivery_customer_view
from .view.for_later_delivery_view import view_for_later_delivery
from .view.future_orders_view import future_orders_view
from .view.telegram_webhook_view import telegram_webhook
from .view.recreate_order_view import recreate_order_view
from .view.delivery_costumer_view import (customer_orders_view, customer_detail_view, 
                                          order_detail_view, delete_selected_orders_view,
                                          delete_uncompleted_orders_view
                                        )
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
    path('delivery_process/<str:delivery_type>/', delivery_process_view, name='delivery_process'),
    path('check_delivery_number/<str:delivery_type>/', delivery_view, name='check_delivery_number'),
    path('add_delivery_customer/<str:delivery_phone_number>/<str:delivery_type>/', add_delivery_customer_view, name='add_delivery_customer'),
    path('save_delivery_customer_changes/<str:delivery_phone_number>/<str:delivery_type>/', save_delivery_customer_changes_view, {'edit': True}, name='save_delivery_customer_changes'),
    path('check_delivery_customer/<str:delivery_phone_number>/<str:delivery_type>/', check_delivery_customer_view, name='check_delivery_customer'),
    path('delivery_add_to_cart/<str:delivery_phone_number>/<str:category>/<str:delivery_type>/', delivery_add_to_cart_view, name='delivery_add_to_cart'),
    path('delivery_menu/<str:delivery_phone_number>/<str:category>/<str:delivery_type>/', delivery_menu_view, name='delivery_menu'),
    path('delivery_pdf_template/<str:delivery_phone_number>/<int:order_id>/', delivery_pdf_template_view, name='delivery_pdf_template'),
    path('delivery_close_cart/<str:delivery_phone_number>/<int:order_id>/', delivery_close_cart_view, name='delivery_close_cart'),
    path('delivery_print_kitchen/', delivery_print_kitchen, name='delivery_print_kitchen'),
    path('delivery_search/<str:delivery_phone_number>/', delivery_search_view, name='delivery_search_products'),
    path('delivery_empty_cart/<str:delivery_phone_number>/<str:delivery_type>/', delivery_empty_cart_view, name='delivery_empty_cart' ),
    path('cart/<str:delivery_phone_number>/<str:delivery_type>/', delivery_cart_view, name='delivery_cart'),
    path('cart/<str:delivery_phone_number>/<str:delivery_type>/increase/<int:product_id>/', delivery_increase_product_view, name='delivery_increase_product'),
    path('cart/<str:delivery_phone_number>/<str:delivery_type>/decrease/<int:product_id>/', delivery_decrease_product_view, name='delivery_decrease_product'),
    path('cart/<str:delivery_phone_number>/<str:delivery_type>/remove/<int:product_id>/', delivery_remove_product_view, name='delivery_remove_product'),
    path('set_courier/<str:delivery_phone_number>/<str:delivery_type>/', set_courier, name='set_courier'),
    path('clear_solo_debt/', clear_solo_debt, name='clear_solo_debt'),
    path('delivery_summary/', delivery_summary, name='delivery_summary'),
    path('later_delivery/<str:delivery_phone_number>/<str:delivery_type>/', view_for_later_delivery, name='view_for_later_delivery'),

    path('future-orders/', future_orders_view, name='future_orders'),

    path('telegram_webhook/', telegram_webhook, name='telegram_webhook'),
    path('customer-orders/', customer_orders_view, name='customer_orders'),
    path('customer/<int:customer_id>/', customer_detail_view, name='customer_detail'),
    path('delivery_order/<int:order_id>/', order_detail_view, name='order_detail'),
    path('recreate_order/<int:order_id>/', recreate_order_view, name='recreate_order'),
    path('delete_selected_orders/<int:customer_id>/', delete_selected_orders_view, name='delete_selected_orders'),
    path('delete_uncompleted_orders/<int:customer_id>/', delete_uncompleted_orders_view, name='delete_uncompleted_orders'),

    path('stas-summary/', stas_summary, name='stas_summary'),


]
