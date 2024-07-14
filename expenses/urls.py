from django.urls import path
from expenses.view.transactions import transaction_list

app_name = 'expenses'

urlpatterns = [
    path('transaction_list', transaction_list, name='transaction_list'),
]