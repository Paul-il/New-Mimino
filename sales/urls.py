from django.urls import path
from .views import statistics_view


urlpatterns = [
    path('statistics/', statistics_view, name='sales_statistics'),
]
