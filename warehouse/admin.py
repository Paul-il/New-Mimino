from django.contrib import admin
from .models import Warehouse, WarehouseItem

class WarehouseAdmin(admin.ModelAdmin):
    pass

admin.site.register(Warehouse, WarehouseAdmin)

class WarehouseItemAdmin(admin.ModelAdmin):
    list_display = ['product', 'warehouse', 'quantity']  # Отображаемые поля
    list_editable = ['quantity']  # Редактируемые поля прямо в списке

admin.site.register(WarehouseItem, WarehouseItemAdmin)
