from django.views.generic import TemplateView
from django.db import models
from django.db.models import Sum, F
from ..models.orders import Order, OrderItem, Product
from django.db.models.functions import ExtractWeekDay
from ..forms import DateRangeForm
from datetime import timedelta
from django.utils import timezone  # Импорт timezone из django.utils
from django.db.models.functions import Cast
from django.db.models import FloatField

class OrderStatisticsView(TemplateView):
    template_name = 'order_statistics.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        date_range_form = DateRangeForm(self.request.GET)
        date_range = None
        if date_range_form.is_valid():
            date_range = date_range_form.cleaned_data['date_range']

        exclude_products = ["Замороженные Хинкали", "Пред оплата"]
        total_sales = OrderItem.objects.exclude(product__product_name_rus__in=exclude_products).aggregate(total=Sum('quantity'))['total']

        product_statistics = OrderItem.objects.values('product__product_name_rus').annotate(
            total_quantity=Sum('quantity'),
            total_price=Sum(F('quantity') * F('product__product_price'), output_field=models.DecimalField()),
            percentage=Cast(Sum('quantity'), FloatField()) / total_sales * 100
        ).order_by('product__product_name_rus')

        product_statistics = product_statistics.exclude(product__product_name_rus__in=exclude_products)

        if date_range:
            start_date = timezone.localtime(timezone.now()) - timedelta(days=int(date_range))
            end_date = timezone.localtime(timezone.now())
            product_statistics = product_statistics.filter(order__created_at__range=[start_date, end_date])
        else:
            first_order = Order.objects.order_by('created_at').first()
            last_order = Order.objects.order_by('created_at').last()
            if first_order and last_order:
                start_date = first_order.created_at
                end_date = last_order.created_at
            else:
                start_date = end_date = None

        selected_category = self.request.GET.get('category')
        if selected_category:
            product_statistics = product_statistics.filter(product__category=selected_category)

        CATEGORY_TRANSLATIONS = dict(Product.CATEGORY_CHOICES)
        translated_categories = [(key, CATEGORY_TRANSLATIONS[key]) for key, _ in Product.CATEGORY_CHOICES]

        total_sales_value = OrderItem.objects.filter(order__created_at__range=[start_date, end_date]).aggregate(
            total_value=Sum(F('quantity') * F('product__product_price'), output_field=models.DecimalField())
        )['total_value']

        context['total_sales_value'] = total_sales_value
        context['selected_category'] = selected_category
        context['product_categories'] = translated_categories
        context['date_range_form'] = date_range_form
        context['product_statistics'] = product_statistics
        context['start_date'] = start_date
        context['end_date'] = end_date

        return context
