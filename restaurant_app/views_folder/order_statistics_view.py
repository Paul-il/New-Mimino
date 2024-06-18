import logging
from django.views.generic import TemplateView
from django.db.models import Sum, F, DecimalField
from django.db.models.functions import Cast
from ..models.orders import Order, OrderItem, Product
from django.db.models import FloatField
from ..forms import CombinedFilterForm
from django.db.models.functions import ExtractWeekDay
from django.utils import timezone
from datetime import timedelta
from django.core.cache import cache

logger = logging.getLogger(__name__)

class OrderStatisticsView(TemplateView):
    template_name = 'order_statistics.html'
    CATEGORY_TRANSLATIONS = dict(Product.CATEGORY_CHOICES)
    EXCLUDE_PRODUCTS = ["Замороженные Хинкали", "Пред оплата", "Скидка", "Скидка на алкоголь"]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = CombinedFilterForm(self.request.GET or None)
        context['form'] = form

        if form.is_valid():
            start_date = form.cleaned_data.get('start_date')
            end_date = form.cleaned_data.get('end_date')
            day_of_week = form.cleaned_data.get('day_of_week')
            category = form.cleaned_data.get('category')
        else:
            start_date = None
            end_date = None
            day_of_week = ''
            category = ''

        try:
            product_statistics = self.get_product_statistics(start_date, end_date, category, day_of_week)
            weekly_sales = self.get_weekly_sales(start_date, end_date, category)
        except Exception as e:
            logger.error(f'Error fetching product statistics: {e}')
            product_statistics = []
            weekly_sales = []

        context.update({
            'form': form,
            'total_sales_value': self.calculate_total_sales_value(start_date, end_date),
            'selected_category': category,
            'selected_day_of_week': day_of_week,
            'product_categories': self.get_translated_categories(),
            'product_statistics': product_statistics,
            'weekly_sales': weekly_sales,
            'start_date': start_date,
            'end_date': end_date
        })

        return context

    def get_product_statistics(self, start_date, end_date, selected_category, selected_day_of_week=None):
        cache_key = f'product_statistics_{start_date}_{end_date}_{selected_category}_{selected_day_of_week}'
        product_statistics = cache.get(cache_key)
        if not product_statistics:
            product_statistics = OrderItem.objects \
                .exclude(product__product_name_rus__in=self.EXCLUDE_PRODUCTS) \
                .values('product__product_name_rus', 'product__id') \
                .annotate(
                    total_quantity=Sum('quantity'),
                    total_price=Sum(F('quantity') * F('product__product_price'), output_field=DecimalField()),
                    percentage=Cast(Sum('quantity'), FloatField()) / self.get_total_sales() * 100
                ).order_by('product__product_name_rus')

            if start_date and end_date:
                product_statistics = product_statistics.filter(order__created_at__range=[start_date, end_date])
            if selected_category:
                product_statistics = product_statistics.filter(product__category=selected_category)
            if selected_day_of_week:
                product_statistics = product_statistics.annotate(day_of_week=ExtractWeekDay('order__created_at')).filter(day_of_week=selected_day_of_week)

            cache.set(cache_key, product_statistics, 60 * 15)  # Кэшируем на 15 минут
        return product_statistics

    def get_weekly_sales(self, start_date, end_date, selected_category):
        cache_key = f'weekly_sales_{start_date}_{end_date}_{selected_category}'
        weekly_sales = cache.get(cache_key)
        if not weekly_sales:
            query = OrderItem.objects.exclude(product__product_name_rus__in=self.EXCLUDE_PRODUCTS)

            if start_date and end_date:
                query = query.filter(order__created_at__range=[start_date, end_date])
            if selected_category:
                query = query.filter(product__category=selected_category)

            weekly_sales = query.annotate(day_of_week=ExtractWeekDay('order__created_at')).values('day_of_week').annotate(
                total_quantity=Sum('quantity')
            ).order_by('day_of_week')

            cache.set(cache_key, weekly_sales, 60 * 15)  # Кэшируем на 15 минут
        return weekly_sales

    def calculate_total_sales_value(self, start_date, end_date):
        if start_date and end_date:
            return OrderItem.objects.filter(order__created_at__range=[start_date, end_date]) \
                .aggregate(
                    total_value=Sum(F('quantity') * F('product__product_price'), output_field=DecimalField())
                )['total_value']
        return None

    def get_total_sales(self):
        return OrderItem.objects \
            .exclude(product__product_name_rus__in=self.EXCLUDE_PRODUCTS) \
            .aggregate(total=Sum('quantity'))['total']

    def get_translated_categories(self):
        return [(key, self.CATEGORY_TRANSLATIONS[key]) for key, _ in Product.CATEGORY_CHOICES]
