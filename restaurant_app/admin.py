from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.db.models import Count, Sum, Q
from django.urls import reverse
from django.utils.html import format_html
from django.db import models
from django.contrib.admin.views.main import ChangeList
from django.contrib.admin import SimpleListFilter

from .models.product import ProductStock, Product, OrderChangeLog
from .models.tables import Table, Booking, Tip, TipDistribution, Room
from .models.orders import Order, Category, PaymentMethod, Transaction

# Ваши остальные импорты

# Классы фильтров

class CategoryFilter(admin.SimpleListFilter):
    title = _('category')
    parameter_name = 'category'

    def lookups(self, request, model_admin):
        categories = set([c.category for c in Product.objects.all()])
        return [(c, c) for c in categories]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(product__category=self.value())

class ActiveOrderFilter(admin.SimpleListFilter):
    title = _('active order')
    parameter_name = 'has_active_order'

    def lookups(self, request, model_admin):
        return (
            ('yes', _('Yes')),
            ('no', _('No')),
        )

    def queryset(self, request, queryset):
        if self.value() == 'yes':
            return queryset.annotate(num_active_orders=Count('orders', filter=models.Q(orders__is_completed=False))).filter(num_active_orders__gt=0)
        if self.value() == 'no':
            return queryset.annotate(num_active_orders=Count('orders')).filter(num_active_orders=0)

# Класс для оптимизации запросов
class OptimizedChangeList(ChangeList):
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('related_field')  # Замените 'related_field' на соответствующее поле

# Регистрация моделей и настройка админ-панели

@admin.register(ProductStock)
class ProductStockAdmin(admin.ModelAdmin):
    list_display = ['product', 'received_quantity', 'received_date']
    list_filter = [CategoryFilter, 'received_date']  # Добавьте здесь свой фильтр
    search_fields = ['product__product_name_rus', 'product__product_name_heb']

    def get_changelist(self, request, **kwargs):
        return OptimizedChangeList

@admin.register(Table)
class TableAdmin(admin.ModelAdmin):
    list_display = ['table_id', 'capacity', 'is_booked', 'are_guests_here', 'num_of_people', 'order_time', 'active_order_link']
    list_filter = [ActiveOrderFilter]  # <--- add the ActiveOrderFilter here

    def active_order_link(self, obj):
        active_order = obj.orders.filter(is_completed=False).first()
        if active_order:
            url = reverse("admin:restaurant_app_order_change", args=[active_order.id])
            return format_html('<a href="{}">{}</a>', url, active_order)
        else:
            return "-"

    active_order_link.short_description = "Active Order"

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "active_order":
            kwargs["queryset"] = Order.objects.filter(table=request.obj, is_completed=False)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'table', 'reserved_date', 'reserved_time', 'num_of_people', 'description', 'are_guests_here', 'is_deleted', 'created_at', 'guests_did_not_arrive']
    list_filter = ['reserved_date', 'is_deleted', 'are_guests_here', 'guests_did_not_arrive']
    search_fields = ['user__username', 'table__table_id', 'description']
    date_hierarchy = 'reserved_date'

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['id', 'product_name_rus', 'product_name_heb', 'product_price', 'category', 'quantity', 'created_at', 'printer']
    list_filter = ['category', 'printer']
    
    def get_product_names(self, obj):
        return f"{obj.product_name} ({obj.product_name_in_hebrew})"
    get_product_names.short_description = 'Product Names'

    def current_stock(self, obj):
        return obj.quantity
    current_stock.short_description = 'Current Stock'

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'table_number', 'total_sum', 'display_cash_amount', 'display_card_amount', 'status', 'payment_method', 'is_confirmed', 'display_is_bill_printed']
    list_filter = ['is_completed', 'created_at', 'created_by', 'is_confirmed']
    fields = ('table', 'created_by', 'created_at', 'is_completed', 
              'comments', 'last_printed_comments', 'table_number', 
              'total_price', 'num_of_people', 'cash_amount', 
              'card_amount', 'status', 'payment_method', 'is_confirmed')

    def display_is_bill_printed(self, obj):
        return obj.is_bill_printed
    display_is_bill_printed.short_description = 'Счет Распечатан'
    display_is_bill_printed.boolean = True

    def display_cash_amount(self, obj):
        return obj.cash_amount if obj.cash_amount is not None else format_html('<span style="color: #999;">-</span>')
    display_cash_amount.short_description = 'Cash Amount'

    def display_card_amount(self, obj):
        return obj.card_amount if obj.card_amount is not None else format_html('<span style="color: #999;">-</span>')
    display_card_amount.short_description = 'Card Amount'

    def products_list(self, obj):
        return ", ".join([f"{item.product.product_name_rus} x{item.quantity}" for item in obj.order_items.all()])
    products_list.short_description = 'Продукты'

    def get_changelist(self, request, **kwargs):
        return OptimizedChangeList

class TipDistributionInline(admin.TabularInline):
    model = TipDistribution
    extra = 0

class UserTipFilter(SimpleListFilter):
    title = 'официант'  # Название фильтра
    parameter_name = 'user'

    def lookups(self, request, model_admin):
        # Возвращает список кортежей. Каждый кортеж содержит (значение_для_фильтрации, человеко-читаемое_название)
        users = set([tip.user for tip in TipDistribution.objects.all()])
        return [(user.id, user.first_name) for user in users]

    def queryset(self, request, queryset):
        # Фильтрует queryset на основе выбранного значения фильтра
        if self.value():
            return queryset.filter(tipdistribution__user__id=self.value())

@admin.register(Tip)
class TipAdmin(admin.ModelAdmin):
    list_display = ['id', 'amount', 'date', 'distributed_to']

    inlines = [TipDistributionInline]
    list_filter = ['date', 'tipdistribution__user']

    def distributed_to(self, obj):
        users = [tip_dist.user for tip_dist in obj.tipdistribution_set.all()]
        links = [format_html('<a href="{}">{}</a>', reverse("admin:auth_user_change", args=[user.id]), user.first_name) for user in users]
        return format_html(", ".join(links))
    
    distributed_to.short_description = "Официанты"

class TableInline(admin.StackedInline):
    model = Table
    extra = 1
    fields = ['table_id', 'capacity']

@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('name',)
    inlines = [TableInline]

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('date', 'type', 'amount', 'payment_method')
    list_filter = ('category', 'payment_method', 'type',)
    ordering = ('-date',)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('category', 'payment_method')

    def changelist_view(self, request, extra_context=None):
        queryset = self.get_queryset(request)
        total_income = queryset.filter(type=Transaction.INCOME).aggregate(total=models.Sum('amount'))['total'] or 0
        if extra_context is None:
            extra_context = {}
        extra_context['total_income'] = total_income
        return super().changelist_view(request, extra_context=extra_context)
    

@admin.register(OrderChangeLog)
class OrderChangeLogAdmin(admin.ModelAdmin):
    list_display = ('order', 'product_name', 'action', 'change_time', 'get_changed_by')

    def get_changed_by(self, obj):
        return obj.changed_by.first_name if obj.changed_by else '-'
    get_changed_by.short_description = 'Изменил'

    # Если нужно, добавьте настройку queryset для оптимизации запросов
    def get_queryset(self, request):
        queryset = super().get_queryset(request).select_related('changed_by')
        return queryset

# Регистрация дополнительных моделей и настройка кастомных представлений, если они есть
admin.site.register(Category)
admin.site.register(PaymentMethod)
