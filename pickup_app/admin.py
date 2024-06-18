from django.contrib import admin
import json
from django.utils.html import format_html
from .models import PickupOrder, Cart, CartItem


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 1

class CartInline(admin.TabularInline):
    model = Cart
    extra = 0

class PickupOrderAdmin(admin.ModelAdmin):
    list_display = ('phone', 'name', 'date_created', 'is_completed', 'status', 'payment_method', 'get_orders_count', 'get_cart_total', 'get_cart_snapshot_display')
    list_filter = ('is_completed', 'status', 'payment_method')
    search_fields = ('phone', 'name', 'status', 'payment_method')
    readonly_fields = ('phone', 'name', 'total_amount', 'status', 'date_created', 'date_updated', 'previous_orders_total_display', 'get_cart_snapshot_display', 'payment_method')

    def get_cart_snapshot_display(self, obj):
        if obj.cart_snapshot:
            cart_snapshot = json.loads(obj.cart_snapshot)
            # Формируем список строк с информацией о каждом товаре
            snapshot_lines = [f"{item['product_name']} - {item['total']}₪" for item in cart_snapshot]
            # Объединяем строки в одну строку, разделяя их переносами строки
            formatted_snapshot = "\n".join(snapshot_lines)
            return formatted_snapshot
        return 'No snapshot'
    get_cart_snapshot_display.short_description = 'Cart Snapshot'

    def get_cart_items_display(self, obj):
        items = []
        carts = obj.carts.all()
        for cart in carts:
            for cart_item in cart.cart_items.all():
                product_price = cart_item.product.product_price
                total_price_for_item = product_price * cart_item.quantity
                items.append(f"{cart_item.product} ({cart_item.quantity}) - {total_price_for_item}₪")
        return "\n".join(items)
    get_cart_items_display.short_description = 'Cart Items'

    def previous_orders_total_display(self, obj):
        return f"{obj.previous_orders_total():,.2f}"
    previous_orders_total_display.short_description = "Сумма предыдущих заказов"

    def get_cart_total(self, obj):
        total = 0
        carts = obj.carts.all()
        for cart in carts:
            for cart_item in cart.cart_items.all():
                product_price = cart_item.product.product_price
                total_price_for_item = product_price * cart_item.quantity
                total += total_price_for_item
        return total
    get_cart_total.short_description = 'Total'

    def get_orders_count(self, obj):
        return PickupOrder.objects.filter(phone=obj.phone).count()
    get_orders_count.short_description = 'Orders Count'

    def payment_method(self, obj):
        return obj.payment_method or "Не указан"
    payment_method.short_description = 'Метод Оплаты'


class CartAdmin(admin.ModelAdmin):
    inlines = [CartItemInline]
    list_display = ('pickup_order', 'created_at', 'total_price')

class CartItemAdmin(admin.ModelAdmin):
    list_display = ('cart', 'product', 'quantity')

admin.site.register(PickupOrder, PickupOrderAdmin)

