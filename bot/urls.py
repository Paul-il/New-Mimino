from django.urls import path
from .views_folder import (unavailable_products_view, order_summary_view, 
                           tip_summary_view, table_summary_view, 
                           delivery_summary_view, booking_summary_view,
                           available_booking_dates_view)

urlpatterns = [
    path('api/unavailable_products/', unavailable_products_view.api_unavailable_products, name='api_unavailable_products'),
    path('api/order_summary/', order_summary_view.api_order_summary, name='api_order_summary'),
    path('api/tip_summary/', tip_summary_view.api_tip_summary, name='api_tip_summary'),
    path('api/table_summary/', table_summary_view.api_table_summary, name='api_table_summary'),
    path('api/delivery_summary/', delivery_summary_view.api_delivery_summary, name='api_delivery_summary'),
    path('api/booking_summary/', booking_summary_view.api_booking_summary),
    path('api/available_booking_dates/', available_booking_dates_view.api_available_booking_dates),
]
