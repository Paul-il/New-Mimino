import logging
import calendar
from datetime import timedelta

from django.views.generic import TemplateView
from django.db.models import Sum, F, DecimalField, FloatField
from django.db.models.functions import Cast, ExtractWeekDay
from ..models.orders import OrderItem, Product
from ..forms import CombinedFilterForm
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

        days_with_dates = self.get_days_with_dates(start_date, end_date) if start_date and end_date and (end_date - start_date).days <= 7 else []

        context.update({
            'form': form,
            'total_sales_value': self.calculate_total_sales_value(start_date, end_date),
            'selected_category': category,
            'selected_day_of_week': day_of_week,
            'product_categories': self.get_translated_categories(),
            'product_statistics': product_statistics,
            'weekly_sales': weekly_sales,
            'start_date': start_date,
            'end_date': end_date,
            'days_of_week': self.get_days_of_week(),
            'days_with_dates': days_with_dates
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

            # Преобразуем результат в список для удобства отображения
            weekly_sales_dict = {day['day_of_week']: day['total_quantity'] for day in weekly_sales}
            weekly_sales = [weekly_sales_dict.get(i, 0) for i in range(1, 8)]  # Дни недели от 1 (Понедельник) до 7 (Воскресенье)

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

    def get_days_of_week(self):
        days_of_week = list(calendar.day_name)
        days_of_week_rus = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье']
        return days_of_week_rus

    def get_days_with_dates(self, start_date, end_date):
        delta = end_date - start_date
        days_with_dates = []
        for i in range(delta.days + 1):
            day_date = start_date + timedelta(days=i)
            day_name = calendar.day_name[day_date.weekday()]
            days_with_dates.append(f"{day_name} ({day_date.strftime('%d-%m-%Y')})")
        return days_with_dates
