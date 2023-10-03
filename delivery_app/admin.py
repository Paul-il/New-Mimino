from django.contrib import admin
from django.utils import timezone
from .models import DeliveryCustomer, DeliveryOrder, DeliveryProduct, DeliveryCart, DeliveryCartItem, Courier
from datetime import timedelta


def mark_as_completed(modeladmin, request, queryset):
    week_ago = timezone.now() - timedelta(days=7)
    queryset.filter(created_at__lte=week_ago, is_completed=False).update(is_completed=True)


class DeliveryCartItemInline(admin.TabularInline):
    model = DeliveryCartItem
    extra = 1


@admin.register(DeliveryCart)
class DeliveryCartAdmin(admin.ModelAdmin):
    list_display = ('id', 'delivery_order', 'customer', 'total_price', 'created_at')
    list_filter = ('delivery_order__is_completed', 'delivery_order__customer__city', 'created_at')
    search_fields = ('delivery_order__customer__name', 'customer__name', 'delivery_order__customer__delivery_phone_number')
    inlines = [DeliveryCartItemInline]
    ordering = ('-created_at',)


@admin.register(DeliveryCustomer)
class DeliveryCustomerAdmin(admin.ModelAdmin):
    list_display = ('delivery_phone_number', 'name', 'city', 'street', 'house_number', 'floor', 'apartment_number', 'intercom_code')
    list_filter = ('city',)


class DeliveryProductInline(admin.TabularInline):
    model = DeliveryProduct
    extra = 1


@admin.register(DeliveryOrder)
class DeliveryOrderAdmin(admin.ModelAdmin):
    list_display = ('pk', 'customer', 'courier', 'formatted_created_at', 'total_amount', 'payment_method', 'is_completed')
    list_filter = ('is_completed', 'customer__city', 'courier', 'payment_method')
    search_fields = ('customer__name', 'customer__delivery_phone_number')
    mark_as_completed.short_description = "Отметить заказы старше недели как выполненные"
    actions = [mark_as_completed]
    inlines = [DeliveryProductInline]

    def formatted_created_at(self, obj):
        local_dt = timezone.localtime(obj.created_at)
        return local_dt.strftime('%Y-%m-%d %H:%M')
    
    formatted_created_at.admin_order_field = 'created_at'
    formatted_created_at.short_description = 'Дата создания'


class DeliveryProductAdmin(admin.ModelAdmin):
    list_display = ('get_customer_phone_number', 'product', 'quantity', 'timestamp')
    list_filter = ('timestamp',)
    search_fields = ('product__name', 'delivery_customer__name')

    def get_customer_phone_number(self, obj):
        return obj.delivery_customer.delivery_phone_number

    get_customer_phone_number.short_description = 'Customer Phone Number'


@admin.register(Courier)
class CourierAdmin(admin.ModelAdmin):
    list_display = ('name', 'delivery_address', 'delivery_city', 'delivery_amount', 'payment_method')
    list_filter = ('delivery_city', 'payment_method')
