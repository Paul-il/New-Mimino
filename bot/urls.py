from django.urls import path
from .views_folder import unavailable_products_view, order_summary_view, tip_summary_view, table_summary_view

urlpatterns = [
    path('api/order_summary/', order_summary_view.api_order_summary, name='api_order_summary'),
    path('api/tip_summary/', tip_summary_view.api_tip_summary, name='api_tip_summary'),
    path('api/table_summary/', table_summary_view.api_table_summary, name='api_table_summary'),
    path('api/unavailable_products/', unavailable_products_view.api_unavailable_products, name='api_unavailable_products'),
]
