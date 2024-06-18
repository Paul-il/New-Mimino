from django.views.generic import TemplateView
from django.db.models import Sum, F, DecimalField
from django.db.models.functions import Cast
from ..models.orders import Order, OrderItem, Product
from django.db.models import FloatField
from ..forms import DateRangeForm
from django.db.models.functions import ExtractWeekDay
from django.utils import timezone
from datetime import timedelta

class OrderStatisticsView(TemplateView):
    template_name = 'order_statistics.html'
    CATEGORY_TRANSLATIONS = dict(Product.CATEGORY_CHOICES)
    EXCLUDE_PRODUCTS = ["Замороженные Хинкали", "Пред оплата"]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = DateRangeForm(self.request.GET or None)
        print(form.fields['day_of_week'].choices)  # Для отладки
        context['form'] = form
        date_range_form = DateRangeForm(self.request.GET or None)
        if date_range_form.is_valid():
            start_date, end_date = self.get_date_range(date_range_form)
        else:
            start_date, end_date = None, None

        selected_category = self.request.GET.get('category', '')
        selected_day_of_week = self.request.GET.get('day_of_week', '')

        product_statistics = self.get_product_statistics(start_date, end_date, selected_category, selected_day_of_week)

        context.update({
            'form': date_range_form,
            'total_sales_value': self.calculate_total_sales_value(start_date, end_date),
            'selected_category': selected_category,
            'selected_day_of_week': selected_day_of_week,
            'product_categories': self.get_translated_categories(),
            'product_statistics': product_statistics,
            'start_date': start_date,
            'end_date': end_date
        })

        return context

    def get_date_range(self, date_range_form):
        if date_range_form.is_valid():
            date_range = date_range_form.cleaned_data.get('date_range')
            if date_range and date_range.isdigit():  # Проверка, является ли date_range числом
                start_date = timezone.localtime(timezone.now()) - timedelta(days=int(date_range))
                end_date = timezone.localtime(timezone.now())
                return start_date, end_date
        # Возвращаем значения по умолчанию, если форма невалидна или date_range не число
        first_order = Order.objects.order_by('created_at').first()
        last_order = Order.objects.order_by('created_at').last()
        if first_order and last_order:
            return first_order.created_at, last_order.created_at
        return None, None


    def get_product_statistics(self, start_date, end_date, selected_category, selected_day_of_week=None):
        product_statistics = OrderItem.objects \
            .exclude(product__product_name_rus__in=self.EXCLUDE_PRODUCTS) \
            .values('product__product_name_rus') \
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

        return product_statistics

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
