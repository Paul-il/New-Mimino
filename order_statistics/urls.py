from django.urls import path
from .views import daily_orders

app_name = 'order_statistics'

urlpatterns = [
    path('daily-orders/', daily_orders, name='daily-orders'),
]
