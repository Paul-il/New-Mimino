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
    list_display = ('phone', 'name', 'date_created', 'is_completed', 'status', 'total_amount', 'get_orders_count', 'get_cart_total')
    list_filter = ('is_completed', 'status')
    search_fields = ('phone', 'name', 'status')
    readonly_fields = ('get_order_items_display', 'get_cart_items_display', 'get_cart_total', 'date_created', 'date_updated')
    list_editable = ('status',)  # позволяет редактировать статус прямо из списка
    readonly_fields = ('get_order_items_display', 'get_cart_items_display', 'get_cart_total', 'date_created', 'date_updated', 'previous_orders_total_display')


    def get_order_items_display(self, obj):
        items = obj.orderitem_set.all()  # используйте orderitem_set для доступа к связанным элементам заказа
        return "\n".join([f"{item.product} ({item.quantity})" for item in items])
    get_order_items_display.short_description = 'Order Items'

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


class CartAdmin(admin.ModelAdmin):
    inlines = [CartItemInline]
    list_display = ('pickup_order', 'created_at', 'total_price')

class CartItemAdmin(admin.ModelAdmin):
    list_display = ('cart', 'product', 'quantity')

admin.site.register(PickupOrder, PickupOrderAdmin)
admin.site.register(Cart, CartAdmin)
admin.site.register(CartItem, CartItemAdmin)
