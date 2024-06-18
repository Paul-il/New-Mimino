from django.views.generic import DetailView
from django.db.models import Sum, F, DecimalField
from ..models.orders import OrderItem, Product
from django.utils import timezone
from datetime import timedelta
from ..forms import CombinedFilterForm
from django.db.models.functions import ExtractWeekDay

class ProductDetailView(DetailView):
    model = Product
    template_name = 'product_detail.html'
    context_object_name = 'product'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.get_object()
        form = CombinedFilterForm(self.request.GET or None)

        if form.is_valid():
            start_date = form.cleaned_data.get('start_date')
            end_date = form.cleaned_data.get('end_date')
        else:
            today = timezone.now().date()
            start_date = today - timedelta(days=6)  # За последние 7 дней
            end_date = today

        context['form'] = form
        context['daily_sales'] = self.get_sales_data(product, start_date, end_date)
        context['weekly_sales'] = self.get_weekly_sales(product, start_date, end_date)

        return context

    def get_sales_data(self, product, start_date, end_date):
        sales_data = OrderItem.objects.filter(
            product=product,
            order__created_at__date__range=[start_date, end_date]
        ).aggregate(
            total_quantity=Sum('quantity'),
            total_price=Sum(F('quantity') * F('product__product_price'), output_field=DecimalField())
        )
        sales_data['start_date'] = start_date
        sales_data['end_date'] = end_date
        return sales_data

    def get_weekly_sales(self, product, start_date, end_date):
        weekly_sales = OrderItem.objects.filter(
            product=product,
            order__created_at__date__range=[start_date, end_date]
        ).annotate(day_of_week=ExtractWeekDay('order__created_at')).values('day_of_week').annotate(
            total_quantity=Sum('quantity')
        ).order_by('day_of_week')
        return weekly_sales
