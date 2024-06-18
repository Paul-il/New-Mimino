from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect

from django.conf.urls import handler404

from restaurant_app.views_folder.cabinet import (personal_cabinet, change_password, edit_profile)
from restaurant_app.views_folder.message_view import (inbox, send_message, unread_messages_count, 
                                                      delete_all_messages,delete_selected_messages, 
                                                      send_link_to_paul,chat_detail,chat_with_user)
from restaurant_app.views_folder.tip_view import tip_view, check_tips
from restaurant_app.views_folder.order_summary import order_summary
from restaurant_app.views_folder.find_product import find_products
from restaurant_app.views_folder.confirm_order_view import confirm_order
from restaurant_app.views_folder.close_table_view import close_table_view
from restaurant_app.views_folder.room_view import rooms_view, room_detail_view
from restaurant_app.views_folder.set_bill_printed_view import set_bill_printed
from restaurant_app.views_folder.recommend_view import recommend_view
from restaurant_app.views_folder.manage_products_view import manage_products, toggle_product_availability
from restaurant_app.views_folder.book_table_view import guests_not_arrived_view, edit_booking_view
from restaurant_app.views_folder.user_summary_view import user_summary, user_detail
from restaurant_app.views_folder.menu_view import menu_view, menu_for_waiter_view
from restaurant_app.views_folder.pdf_view import generate_pdf_view
from restaurant_app.views_folder.kitchen_template import kitchen_template_view, print_kitchen, print_kitchen_for_waiter
from restaurant_app.views_folder.order_statistics_view import OrderStatisticsView
from restaurant_app.views_folder.productdetailview import ProductDetailView
from restaurant_app.views_folder.search_product import search_products
from restaurant_app.views_folder.pdf_template_view import pdf_template_view
from restaurant_app.views_folder.ask_where_views import ask_where_view
from restaurant_app.views_folder.search_view import search_products_view
from restaurant_app.views_folder.login_view import login_page_view, logout_view
from restaurant_app.views_folder.tables_view import tables_view, table_order_view
from restaurant_app.views_folder.table_detail_view import table_detail
from restaurant_app.views_folder.add_stock_view import limited_products_view, update_product_stock
from restaurant_app.views_folder.cart_view import (
    add_to_cart_view, order_detail_view, increase_product_in_order_view,
    decrease_product_from_order_view, get_order_item_quantity_view,
    delete_product_from_order_view,
    empty_order_detail_view, waiter_cart_view, add_product_to_waiter_order_view,
    delete_product_from_waiter_order_view,delete_waiter_order_and_items_view, password_check_view, 
    apply_discount_view, update_delivery_status
)

from restaurant_app.views import (
    book_table_view, bookings_view, guests_here_view,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', login_page_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('ask_where', ask_where_view, name='ask_where'),
    path('table/<int:table_id>/', table_order_view, name='table_order_view'),
    path('tables/', tables_view, name='tables'),
    path('tables/<int:room_id>/', tables_view, name='tables'),
    path('table_detail/<int:table_id>/<int:order_id>/', table_detail, name='table_detail'),
    path('apply_discount/', apply_discount_view, name='apply_discount'),

    path('rooms/', rooms_view, name='rooms'),
    path('room/<int:room_id>/', room_detail_view, name='room_detail'),
    path('room/<int:room_id>/tables/', tables_view, name='tables_in_room'),

    path('order/<int:order_id>/password-check/<str:action>/<int:order_item_id>/', password_check_view, name='password_check'),
    path('confirm-order/<int:order_id>', confirm_order, name='confirm-order'),

    path('search', search_products_view, name='search_products'),
    path('search-products/', search_products, name='search_products'),

    path('expenses/', include('expenses.urls')),
    path('pickup/', include('pickup_app.urls')),

    path('', include('delivery_app.urls')),

    path('sales/', include('sales.urls')),
   

    path('book_table/', book_table_view, name='book_table'),
    path('bookings/', bookings_view, name='bookings'),
    path('edit_booking/<int:booking_id>/', edit_booking_view, name='edit_booking'),
    path('guests_here/<int:booking_id>/', guests_here_view, name='guests_here'),
    path('guests_not_arrived/<int:booking_id>/', guests_not_arrived_view, name='guests_not_arrived'),
    path('menu/<str:table_id>/<str:category>/', menu_view, name='menu'),

    path('menu_for_waiter/<str:category>/', menu_for_waiter_view, name='menu_for_waiter'),
    path('waiter_cart/', waiter_cart_view, name='waiter_cart'),
    path('add_product_to_waiter_order/<int:product_id>/<int:quantity>/', add_product_to_waiter_order_view, name='add_product_to_waiter_order'),
    path('delete_product_from_waiter_order/<int:waiter_order_id>/<int:order_item_id>/', delete_product_from_waiter_order_view, name='delete_product_from_waiter_order'),
    path('delete_waiter_order_and_items/<int:waiter_order_id>/', delete_waiter_order_and_items_view, name='delete_waiter_order_and_items'),
    path('print_kitchen_for_waiter/', print_kitchen_for_waiter, name='print_kitchen_for_waiter'),
    
    path('table_order/<int:table_id>/', table_order_view, name='table_order'),
    path('cart_detail/<int:order_id>/', order_detail_view, name='cart_detail'),

    path('empty_order_detail/', empty_order_detail_view, name='empty_order_detail'),

    path('print_kitchen/', print_kitchen, name='print_kitchen'),
    path('set_bill_printed/<int:order_id>/', set_bill_printed, name='set_bill_printed'),

    path('order/<int:order_id>/', order_detail_view, name='cart_detail'),

    path('kitchen_template/<int:order_id>/', kitchen_template_view, name='kitchen_template'),
    path('pdf_template/<int:order_id>/', pdf_template_view, name='pdf_template'),

    path('add_to_cart/<str:table_id>/', add_to_cart_view, name='add_to_cart'),
    path('generate-pdf/<int:order_id>/', generate_pdf_view, name='generate_pdf'),
    path('order/<int:order_id>/add/<int:order_item_id>/', increase_product_in_order_view, name='increase_product_in_order'),
    path('order/<int:order_id>/remove/<int:order_item_id>/', decrease_product_from_order_view, name='decrease_product_from_order'),
    path('order/<int:order_id>/order_item/<int:order_item_id>/quantity/', get_order_item_quantity_view, name='get_order_item_quantity'),
    path('order/<int:order_id>/delete/<int:order_item_id>/', delete_product_from_order_view, name='delete_product_from_order'),

    path('order-item/<int:order_item_id>/update-delivery-status/', update_delivery_status, name='update_delivery_status'),

    path('order_statistics/', OrderStatisticsView.as_view(), name='order_statistics'),
    path('product/<int:pk>/', ProductDetailView.as_view(), name='product_detail'),
    path('tip/<int:table_id>/', tip_view, name='tip'),
    path('check_tips/', check_tips, name='check_tips'),
    path('close_table/', close_table_view, name='close_table'),

    path('user_summary/', user_summary, name='user_summary'),
    path('user_summary/<int:user_id>/', user_detail, name='user_detail'),

    path('order_summary/', order_summary, name='order_summary'),

    path('manage_products/', manage_products, name='manage_products'),
    path('toggle_product/', toggle_product_availability, name='toggle_product_availability'),
    path('recommendations/<int:order_id>/', recommend_view, name='recommendations'),

    path('find_products/', find_products, name='find_products'),

    path('personal-cabinet/', personal_cabinet, name='personal_cabinet'),
    path('personal-cabinet/change-password/', change_password, name='change_password'),
    path('personal-cabinet/edit-profile/', edit_profile, name='edit_profile'),
    path('inbox/', inbox, name='inbox'),
    path('chat/<int:chat_id>/', chat_detail, name='chat_detail'),
    path('chat_with_user/<int:user_id>/', chat_with_user, name='chat_with_user'),
    path('send_message/', send_message, name='send_message'),
    path('send_message/<int:chat_id>/', send_message, name='send_message'),
    path('delete_selected_messages/<int:chat_id>/', delete_selected_messages, name='delete_selected_messages'),
    path('delete_all_messages/<int:chat_id>/', delete_all_messages, name='delete_all_messages'),
    path('unread_messages_count/', unread_messages_count, name='unread_messages_count'),
    path('send_link_to_paul/', send_link_to_paul, name='send_link_to_paul'),

    path('limited-products/', limited_products_view, name='limited_products'),
    path('update-product-stock/<int:product_id>/', update_product_stock, name='update_product_stock'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

from django.views.generic import RedirectView
urlpatterns += [
    path('favicon.ico', RedirectView.as_view(url=settings.STATIC_URL + 'favicon.ico')),
]

def custom_404_view(request, exception):
    if request.user.is_authenticated:
        return redirect('ask_where')
    else:
        return redirect('login')

handler404 = custom_404_view
