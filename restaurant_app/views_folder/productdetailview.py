import logging
import calendar
from datetime import timedelta, datetime
from django.utils.timezone import make_aware
from django.views.generic import TemplateView
from django.db.models import Sum, F, DecimalField, FloatField
from django.db.models.functions import Cast, ExtractWeekDay
from ..models.orders import OrderItem, Product
from ..forms import CombinedFilterForm
from django.core.cache import cache

logger = logging.getLogger(__name__)

class ProductDetailView(TemplateView):
    template_name = 'product_detail.html'
    CATEGORY_TRANSLATIONS = dict(Product.CATEGORY_CHOICES)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product_id = self.kwargs.get('pk')
        product = Product.objects.get(id=product_id)
        form = CombinedFilterForm(self.request.GET or None)
        context['form'] = form

        if form.is_valid():
            start_date = form.cleaned_data.get('start_date')
            end_date = form.cleaned_data.get('end_date')
            if start_date:
                start_date = make_aware(datetime.combine(start_date, datetime.min.time()))
            if end_date:
                end_date = make_aware(datetime.combine(end_date, datetime.min.time()))
        else:
            start_date = None
            end_date = None

        try:
            daily_sales = self.get_daily_sales(product_id, start_date, end_date)
            weekly_sales = self.get_weekly_sales(product_id, start_date, end_date)
        except Exception as e:
            logger.error(f'Error fetching sales statistics: {e}')
            daily_sales = {}
            weekly_sales = []

        if start_date and end_date and (end_date - start_date).days <= 7:
            days_with_dates, sales_data = self.get_days_with_dates(start_date, end_date, weekly_sales)
        else:
            days_with_dates, sales_data = self.get_days_of_week(), weekly_sales

        context.update({
            'product': product,
            'form': form,
            'daily_sales': daily_sales,
            'weekly_sales': sales_data,
            'days_with_dates': days_with_dates,
            'start_date': start_date,
            'end_date': end_date,
        })

        logger.debug(f"Context Data: {context}")

        return context

    def get_daily_sales(self, product_id, start_date, end_date):
        query = OrderItem.objects.filter(product_id=product_id)
        if start_date and end_date:
            query = query.filter(order__created_at__range=[start_date, end_date])
        return query.aggregate(
            total_quantity=Sum('quantity'),
            total_price=Sum(F('quantity') * F('product__product_price'), output_field=DecimalField())
        )

    def get_weekly_sales(self, product_id, start_date, end_date):
        query = OrderItem.objects.filter(product_id=product_id)
        if start_date and end_date:
            query = query.filter(order__created_at__range=[start_date, end_date])
        weekly_sales = query.annotate(day_of_week=ExtractWeekDay('order__created_at')).values('day_of_week').annotate(
            total_quantity=Sum('quantity')
        ).order_by('day_of_week')

        # Преобразуем результат в список для удобства отображения
        weekly_sales_dict = {day['day_of_week']: day['total_quantity'] for day in weekly_sales}
        # Создаем словарь с ключами от 1 до 7 для всех дней недели, начиная с воскресенья
        all_days = {i: 0 for i in range(1, 8)}
        all_days.update(weekly_sales_dict)
        # Преобразуем значения в список, начиная с воскресенья (воскресенье - день 1)
        weekly_sales = [all_days[7]] + [all_days[i] for i in range(1, 7)]

        return weekly_sales

    def get_days_with_dates(self, start_date, end_date, weekly_sales):
        delta = end_date - start_date
        days_with_dates = []
        sales_data = []

        for i in range(delta.days + 1):
            day_date = start_date + timedelta(days=i)
            day_name = calendar.day_name[day_date.weekday()]
            days_with_dates.append(f"{day_name} ({day_date.strftime('%d-%m-%Y')})")

            day_of_week = (day_date.weekday() + 1) % 7 + 1
            sales_data.append(weekly_sales[day_of_week - 1])

        logger.debug(f"Days with Dates: {days_with_dates}")
        logger.debug(f"Sales Data: {sales_data}")

        return days_with_dates, sales_data

    def get_days_of_week(self):
        days_of_week = ['Воскресенье', 'Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота']
        return days_of_week, [0] * 7
