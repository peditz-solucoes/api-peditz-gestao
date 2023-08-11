from django.contrib import admin
from .models import (
    Cashier, 
    Bill,
    Order,
    PaymentMethod,
    Payment,
    OrderComplement,
    OrderComplementItem,
    OrderStatus,
    OrderGroup,
    TakeoutOrder,
    PaymentGroup,
)
# Register your models here.


class OderComplementsFieldsInline(admin.TabularInline):
    model = OrderComplement
class OderComplementsItemsFieldsInline(admin.TabularInline):
    model = OrderComplementItem

class OderFieldsInline(admin.TabularInline):
    model = Order
    readonly_fields = ['unit_price', 'product_title']
    inlines = [OderComplementsFieldsInline]

class OrderGroupInline(admin.TabularInline):
    model = OrderGroup
    readonly_fields = ['id', 'order_number', 'collaborator_name', 'total']

@admin.register(Cashier)
class CashierAdmin(admin.ModelAdmin):
    pass

@admin.register(Bill)
class BillAdmin(admin.ModelAdmin):
    inlines = [OrderGroupInline]

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    inlines = [OderComplementsFieldsInline]

@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    pass

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    pass
@admin.register(OrderComplement)
class OrderComplementAdmin(admin.ModelAdmin):
    inlines = [OderComplementsItemsFieldsInline]

@admin.register(OrderComplementItem)
class OrderComplementItemAdmin(admin.ModelAdmin):
    pass

@admin.register(OrderStatus)
class OrderStatusAdmin(admin.ModelAdmin):
    pass

@admin.register(OrderGroup)
class OrderGroupAdmin(admin.ModelAdmin):
    readonly_fields = ['id', 'order_number', 'collaborator_name']
    inlines = [OderFieldsInline]

@admin.register(TakeoutOrder)
class TakeoutOrderAdmin(admin.ModelAdmin):
    pass

class PaymentInline(admin.TabularInline):
    model = Payment

class BillsInline(admin.TabularInline):
    model = Bill
    fields = ['number', 'open', 'client_name']
@admin.register(PaymentGroup)
class PaymentGroupAdmin(admin.ModelAdmin):
    inlines = [BillsInline,PaymentInline]

