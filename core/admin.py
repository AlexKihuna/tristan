from django.contrib import admin
from .models import (
    Customer, SalesOrder, Inventory, ItemImage, SalesOrderItem,
    SalesOrderPayment, Supplier, SupplyOrder, SupplyOrderItem,
    SupplyOrderPayment
)


class CustomerAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'contact_phone')
    search_fields = ('name', 'email', 'contact_phone')


class ItemImageInline(admin.StackedInline):
    model = ItemImage


class InventoryAdmin(admin.ModelAdmin):
    list_display = ('item_name', 'item_sku', 'has_stock')
    search_fields = ('item_name', 'item_sku')
    readonly_fields = ('has_stock',)
    inlines = (ItemImageInline, )


class SalesOrderItemInline(admin.StackedInline):
    model = SalesOrderItem

class SalesOrderPaymentInline(admin.StackedInline):
    model = SalesOrderPayment


class SalesOrderAdmin(admin.ModelAdmin):
    list_display = ('order_code', 'get_customer', 'get_item_count')
    search_fields = ('order_code', 'get_customer', )
    inlines = (SalesOrderItemInline, SalesOrderPaymentInline)

    def get_item_count(self, inst):
        return inst.salesorderitem_set.count()
    get_item_count.short_description = 'Number of Items'

    def get_customer(self, obj):
        return obj.customer.name
    get_customer.short_description = 'Customer'
    get_customer.admin_order_field = 'customer__name'


class SupplierOrderAdmin(admin.ModelAdmin):
    list_display = ('order_code', 'get_supplier', 'get_item_count')
    search_fields = ('order_code', 'get_supplier', )
    inlines = (SalesOrderItemInline, SalesOrderPaymentInline)

    def get_item_count(self, inst):
        return inst.salesorderitem_set.count()
    get_item_count.short_description = 'Number of Items'

    def get_supplier(self, obj):
        return obj.customer.name
    get_supplier.short_description = 'Customer'
    get_supplier.admin_order_field = 'customer__name'


admin.site.register(Customer, CustomerAdmin)
admin.site.register(Supplier, CustomerAdmin)
admin.site.register(Inventory, InventoryAdmin)
admin.site.register(SalesOrder, SalesOrderAdmin)
