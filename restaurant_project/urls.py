from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from restaurant_app.views_folder.menu_view import menu_view
from restaurant_app.views_folder.pdf_view import generate_pdf_view
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
    path('tables/', tables_view, name='tables'),

    path('search', search_products_view, name='search_products'),

    
    path('pickup/', include('pickup_app.urls')),

    path('', include('delivery_app.urls')),
   
    path('book_table/<int:table_id>/', book_table_view, name='book_table'),
    path('bookings/', bookings_view, name='bookings'),
    path('guests_here/<int:booking_id>/', guests_here_view, name='guests_here'),
    path('menu/<str:table_id>/<str:category>/', menu_view, name='menu'),

    path('table_order/<int:table_id>/', table_order_view, name='table_order'),
    path('order_detail/<int:order_id>/', order_detail_view, name='order_detail'),

    path('empty_order_detail/', empty_order_detail_view, name='empty_order_detail'),

    path('add_to_cart/<str:table_id>/', add_to_cart_view, name='add_to_cart'),
    path('generate_pdf/<int:order_id>/', generate_pdf_view, name='generate_pdf'),
    path('order/<int:order_id>/add/<int:order_item_id>/', increase_product_in_order_view, name='increase_product_in_order'),
    path('order/<int:order_id>/remove/<int:order_item_id>/', decrease_product_from_order_view, name='decrease_product_from_order'),
    path('order/<int:order_id>/order_item/<int:order_item_id>/quantity/', get_order_item_quantity_view, name='get_order_item_quantity'),
    path('order/<int:order_id>/delete/<int:order_item_id>/', delete_product_from_order_view, name='delete_product_from_order'),
    path('pay_order/<int:order_id>/', pay_order_view, name='pay_order'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

