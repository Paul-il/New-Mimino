from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.db.models import Count, Sum, Q
from django.urls import reverse
from django.utils.html import format_html
from django.contrib.auth.models import User
from django.contrib.admin.views.main import ChangeList
from django.contrib import messages
from django.db import models
from django.urls import path
from django.http import HttpResponseRedirect
from .models.product import ProductStock, Product, OrderChangeLog
from .models.tables import Table, Booking, Tip, TipDistribution, Room
from .models.orders import Order, Category, PaymentMethod, Transaction

# Базовый класс для фильтров
class BaseFilter(admin.SimpleListFilter):
    def get_lookups_from_queryset(self, queryset, field_name):
        return queryset.values_list(field_name, flat=True).distinct()

class CategoryFilter(BaseFilter):
    title = _('category')
    parameter_name = 'category'

    def lookups(self, request, model_admin):
        return [(c, c) for c in self.get_lookups_from_queryset(Product.objects.all(), 'category')]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(product__category=self.value())

class ActiveOrderFilter(BaseFilter):
    title = _('active order')
    parameter_name = 'has_active_order'

    def lookups(self, request, model_admin):
        return (
            ('yes', _('Yes')),
            ('no', _('No')),
        )

    def queryset(self, request, queryset):
        if self.value() == 'yes':
            return queryset.annotate(num_active_orders=Count('orders', filter=Q(orders__is_completed=False))).filter(num_active_orders__gt=0)
        if self.value() == 'no':
            return queryset.annotate(num_active_orders=Count('orders')).filter(num_active_orders=0)

# Базовый класс для админ-моделей с оптимизированным ChangeList
class BaseAdmin(admin.ModelAdmin):
    def get_changelist(self, request, **kwargs):
        return OptimizedChangeList

# Класс для оптимизации запросов
class OptimizedChangeList(ChangeList):
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # Замените 'table' и 'user' на соответствующие поля для конкретной модели
        if hasattr(self.model, 'table'):
            return qs.select_related('table')
        elif hasattr(self.model, 'user'):
            return qs.select_related('user')
        else:
            return qs

# Регистрация моделей и настройка админ-панели

@admin.register(ProductStock)
class ProductStockAdmin(BaseAdmin):
    list_display = ['product', 'received_quantity', 'received_date']
    list_filter = [CategoryFilter, 'received_date']
    search_fields = ['product__product_name_rus', 'product__product_name_heb']

@admin.register(Table)
class TableAdmin(BaseAdmin):
    list_display = ['table_id', 'capacity', 'is_booked', 'are_guests_here', 'num_of_people', 'order_time', 'active_order_link']
    list_filter = [ActiveOrderFilter]

    def active_order_link(self, obj):
        active_order = obj.orders.select_related('table').filter(is_completed=False).first()
        if active_order:
            url = reverse("admin:restaurant_app_order_change", args=[active_order.id])
            return format_html('<a href="{}">{}</a>', url, active_order)
        else:
            return "-"

    active_order_link.short_description = "Active Order"

@admin.register(Booking)
class BookingAdmin(BaseAdmin):
    list_display = ['id', 'user', 'table', 'reserved_date', 'reserved_time', 'num_of_people', 'description', 'are_guests_here', 'is_deleted', 'created_at', 'guests_did_not_arrive']
    list_filter = ['reserved_date', 'is_deleted', 'are_guests_here', 'guests_did_not_arrive']
    search_fields = ['user__username', 'table__table_id', 'description']
    date_hierarchy = 'reserved_date'

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'product_name_rus', 'product_name_heb', 'product_price', 
        'category', 'quantity', 'created_at', 'printer', 'has_limit', 
        'limit_quantity', 'is_available_for_delivery', 'is_available', 
        'show_in_menu', 'toggle_availability_button'
    ]
    list_filter = ['category', 'printer', 'has_limit', 'is_available_for_delivery', 'is_available', 'show_in_menu']
    search_fields = ['product_name_rus', 'product_name_heb']
    fields = (
        'product_name_rus', 'product_name_heb', 'product_price', 'product_img', 
        'category', 'quantity', 'delivery_price', 'is_available', 
        'preparation_time', 'has_limit', 'limit_quantity', 'is_available_for_delivery',
        'show_in_menu'
    )
    list_editable = ['is_available', 'show_in_menu']

    def toggle_availability_button(self, obj):
        if obj.is_available:
            return format_html('<a class="button" href="{}">Отключить</a>', reverse('admin:toggle_availability', args=[obj.pk]))
        else:
            return format_html('<a class="button" href="{}">Включить</a>', reverse('admin:toggle_availability', args=[obj.pk]))
    toggle_availability_button.short_description = 'Изменить доступность'
    toggle_availability_button.allow_tags = True

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('toggle_availability/<int:pk>/', self.admin_site.admin_view(self.toggle_availability), name='toggle_availability'),
        ]
        return custom_urls + urls

    def toggle_availability(self, request, pk):
        product = self.get_object(request, pk)
        product.is_available = not product.is_available
        product.save()
        self.message_user(request, f"Доступность продукта '{product.product_name_rus}' изменена.")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/admin'))

    def save_model(self, request, obj, form, change):
        if obj.has_limit and not obj.limit_quantity:
            self.message_user(request, 'Установите количество лимита для лимитированного продукта.', level='error')
        else:
            super().save_model(request, obj, form, change)

@admin.register(Order)
class OrderAdmin(BaseAdmin):
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

class TipDistributionInline(admin.TabularInline):
    model = TipDistribution
    extra = 0

class UserTipFilter(BaseFilter):
    title = 'официант'
    parameter_name = 'user'

    def lookups(self, request, model_admin):
        users = User.objects.filter(tipdistribution__isnull=False).distinct()
        return [(user.id, user.first_name) for user in users]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(tipdistribution__user__id=self.value())

@admin.register(Tip)
class TipAdmin(BaseAdmin):
    list_display = ['id', 'amount', 'date', 'distributed_to']

    inlines = [TipDistributionInline]
    list_filter = ['date', UserTipFilter]

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
class RoomAdmin(BaseAdmin):
    list_display = ('name',)
    inlines = [TableInline]

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('date', 'type', 'amount', 'payment_method', 'cash_amount', 'card_amount', 'get_category_name')
    list_filter = ('category', 'payment_method', 'type',)
    ordering = ('-date',)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('category', 'payment_method')

    def get_category_name(self, obj):
        return obj.category.name
    get_category_name.short_description = 'Category'

    def changelist_view(self, request, extra_context=None):
        queryset = self.get_queryset(request)
        total_income = queryset.filter(type=Transaction.INCOME).aggregate(total=Sum('amount'))['total'] or 0
        if extra_context is None:
            extra_context = {}
        extra_context['total_income'] = total_income
        return super().changelist_view(request, extra_context=extra_context)

    # Убедитесь, что поле date использует виджет для выбора даты
    formfield_overrides = {
        models.DateField: {'widget': admin.widgets.AdminDateWidget},
    }

@admin.register(OrderChangeLog)
class OrderChangeLogAdmin(BaseAdmin):
    list_display = ('order', 'product_name', 'action', 'change_time', 'get_changed_by')

    def get_changed_by(self, obj):
        return obj.changed_by.first_name if obj.changed_by else '-'
    get_changed_by.short_description = 'Изменил'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('changed_by')

# Регистрация дополнительных моделей и настройка кастомных представлений, если они есть
admin.site.register(Category)
admin.site.register(PaymentMethod)
