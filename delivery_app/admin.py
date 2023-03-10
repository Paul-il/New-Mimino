from django.contrib import admin

from .models import DeliveryCustomer, DeliveryOrder, DeliveryProduct

from .models import DeliveryCart, DeliveryCartItem

class DeliveryCartItemInline(admin.TabularInline):
    model = DeliveryCartItem
    extra = 1

@admin.register(DeliveryCart)
class DeliveryCartAdmin(admin.ModelAdmin):
    list_display = ('id', 'delivery_order', 'customer', 'total_price', 'created_at')
    list_filter = ('delivery_order__is_completed', 'delivery_order__customer__city')
    search_fields = ('delivery_order__customer__name', 'customer__name')
    inlines = [DeliveryCartItemInline]

@admin.register(DeliveryCustomer)
class DeliveryCustomerAdmin(admin.ModelAdmin):
    list_display = ('delivery_phone_number', 'name', 'city', 'street', 'house_number', 'floor', 'apartment_number', 'intercom_code')
    list_filter = ('city',)


class DeliveryProductInline(admin.TabularInline):
    model = DeliveryProduct
    extra = 1

@admin.register(DeliveryOrder)
class DeliveryOrderAdmin(admin.ModelAdmin):
    list_display = ('pk', 'customer', 'created_at', 'is_completed')
    list_filter = ('is_completed', 'customer__city')
    inlines = [DeliveryProductInline]

class DeliveryProductAdmin(admin.ModelAdmin):
    list_display = ('get_customer_phone_number', 'product', 'quantity', 'timestamp')
    list_filter = ('timestamp',)
    search_fields = ('product__name', 'delivery_customer__name')

    def get_customer_phone_number(self, obj):
        return obj.delivery_customer.delivery_phone_number

    get_customer_phone_number.short_description = 'Customer Phone Number'

