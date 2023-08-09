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

@admin.register(Cashier)
class CashierAdmin(admin.ModelAdmin):
    pass

@admin.register(Bill)
class BillAdmin(admin.ModelAdmin):
    pass

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

@admin.register(TakeoutOrder)
class TakeoutOrderAdmin(admin.ModelAdmin):
    pass