from django.contrib import admin

from .models import PickupOrder, Cart, CartItem


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 1

class CartInline(admin.TabularInline):
    model = Cart
    extra = 0

class PickupOrderAdmin(admin.ModelAdmin):
    inlines = [CartInline]
    list_display = ('phone', 'name', 'date_created', 'is_completed', 'get_orders_count')
    list_filter = ('is_completed',)
    readonly_fields = ('get_order_items_display', 'get_cart_items_display', 'get_cart_total')

    def get_order_items_display(self, obj):
        items = obj.get_order_items()
        return "\n".join([f"{item.product} ({item.quantity})" for item in items])
    get_order_items_display.short_description = 'Order Items'

    def get_cart_items_display(self, obj):
        items = []
        carts = obj.carts.all()
        for cart in carts:
            items.extend([f"{cart_item.product} ({cart_item.quantity})" for cart_item in cart.cart_items.all()])
        return "\n".join(items)
    get_cart_items_display.short_description = 'Cart Items'

    def get_cart_total(self, obj):
        total = 0
        carts = obj.carts.all()
        for cart in carts:
            total += cart.total_price
        return total

    get_cart_total.short_description = 'Total'

    def get_orders_count(self, obj):
        return PickupOrder.objects.filter(phone=obj.phone).count()

    get_orders_count.short_description = 'Orders Count'

class CartAdmin(admin.ModelAdmin):
    inlines = [CartItemInline]
    list_display = ('pickup_order', 'created_at', 'total_price')

class CartItemAdmin(admin.ModelAdmin):
    list_display = ('cart', 'product', 'quantity')

admin.site.register(PickupOrder, PickupOrderAdmin)
admin.site.register(Cart, CartAdmin)
admin.site.register(CartItem, CartItemAdmin)
