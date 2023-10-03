from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.conf.urls import handler404

from restaurant_app.views_folder.tip_view import tip_view, check_tips
from restaurant_app.views_folder.order_summary import order_summary
from restaurant_app.views_folder.close_table_view import close_table_view
from restaurant_app.views_folder.room_view import rooms_view, room_detail_view
from restaurant_app.views_folder.recommend_view import recommend_view
from restaurant_app.views_folder.manage_products_view import manage_products
from restaurant_app.views_folder.book_table_view import guests_not_arrived_view
from restaurant_app.views_folder.user_summary_view import user_summary, user_detail
from restaurant_app.views_folder.menu_view import menu_view
from restaurant_app.views_folder.pdf_view import generate_pdf_view
from restaurant_app.views_folder.kitchen_template import kitchen_template_view, print_kitchen
from restaurant_app.views_folder.order_statistics_view import OrderStatisticsView
from restaurant_app.views_folder.pdf_template_view import pdf_template_view
from restaurant_app.views_folder.ask_where_views import ask_where_view
from restaurant_app.views_folder.search_view import search_products_view
from restaurant_app.views_folder.login_view import login_page_view, logout_view
from restaurant_app.views_folder.tables_view import tables_view, table_order_view
from restaurant_app.views_folder.cart_view import (
    add_to_cart_view, order_detail_view, increase_product_in_order_view,
    decrease_product_from_order_view, get_order_item_quantity_view,
    delete_product_from_order_view, pay_order_view,
    empty_order_detail_view,
)


from restaurant_app.views import (
    book_table_view, bookings_view, guests_here_view,

)

app_name = 'restaurant_app'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', login_page_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('ask_where', ask_where_view, name='ask_where'),
    path('table/<int:table_id>/', table_order_view, name='table_order_view'),
    path('tables/', tables_view, name='tables'),
    path('tables/<int:room_id>/', tables_view, name='tables'),


    path('rooms/', rooms_view, name='rooms'),
    path('room/<int:room_id>/', room_detail_view, name='room_detail'),
    path('room/<int:room_id>/tables/', tables_view, name='tables_in_room'),



    path('search', search_products_view, name='search_products'),

    
    path('pickup/', include('pickup_app.urls')),

    path('', include('delivery_app.urls')),

    path('sales/', include('sales.urls')),
   
    path('book_table/<int:table_id>/', book_table_view, name='book_table'),
    path('bookings/', bookings_view, name='bookings'),
    path('guests_here/<int:booking_id>/', guests_here_view, name='guests_here'),
    path('guests_not_arrived/<int:booking_id>/', guests_not_arrived_view, name='guests_not_arrived'),
    path('menu/<str:table_id>/<str:category>/', menu_view, name='menu'),

    

    path('table_order/<int:table_id>/', table_order_view, name='table_order'),
    path('order_detail/<int:order_id>/', order_detail_view, name='order_detail'),

    path('empty_order_detail/', empty_order_detail_view, name='empty_order_detail'),

    path('/print_kitchen/', print_kitchen, name='print_kitchen'),

    path('kitchen_template/<int:order_id>/', kitchen_template_view, name='kitchen_template'),
    path('pdf_template/<int:order_id>/', pdf_template_view, name='pdf_template'),

    path('add_to_cart/<str:table_id>/', add_to_cart_view, name='add_to_cart'),
    path('generate-pdf/<int:order_id>/', generate_pdf_view, name='generate_pdf'),
    path('order/<int:order_id>/add/<int:order_item_id>/', increase_product_in_order_view, name='increase_product_in_order'),
    path('order/<int:order_id>/remove/<int:order_item_id>/', decrease_product_from_order_view, name='decrease_product_from_order'),
    path('order/<int:order_id>/order_item/<int:order_item_id>/quantity/', get_order_item_quantity_view, name='get_order_item_quantity'),
    path('order/<int:order_id>/delete/<int:order_item_id>/', delete_product_from_order_view, name='delete_product_from_order'),
    path('pay_order/<int:order_id>/', pay_order_view, name='pay_order'),

    path('order_statistics/', OrderStatisticsView.as_view(), name='order_statistics'),
    path('tip/', tip_view, name='tip'),
    path('check_tips/', check_tips, name='check_tips'),
    path('close_table/', close_table_view, name='close_table'),

    path('user_summary/', user_summary, name='user_summary'),
    path('user_summary/<int:user_id>/', user_detail, name='user_detail'),

    path('order_summary/', order_summary, name='order_summary'),

    path('manage_products/', manage_products, name='manage_products'),
    path('recommendations/<int:order_id>/', recommend_view, name='recommendations'),


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