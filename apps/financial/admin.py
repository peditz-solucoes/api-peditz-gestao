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
    CancelationReason
)
# Register your models here.
from django_admin_listfilter_dropdown.filters import ChoiceDropdownFilter, RelatedDropdownFilter, DropdownFilter, SimpleDropdownFilter


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
    list_display = ['number', 'open', 'opened_by_name', 'cashier', 'table', 'created']
    list_filter = [('open', DropdownFilter), ('cashier__restaurant', RelatedDropdownFilter), 'created']
    search_fields = ['number']

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    inlines = [OderComplementsFieldsInline]

@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    pass

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['payment_group', 'value', 'payment_method', 'created']
    list_filter = [('payment_group__cashier__restaurant', RelatedDropdownFilter), ('payment_method', RelatedDropdownFilter), 'created']
    search_fields = ['payment_method_title']
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
    list_display = ['order_number', 'type','bill', 'collaborator_name', 'total', 'created', 'status']
    list_filter = [('status', DropdownFilter), ('restaurant', RelatedDropdownFilter), ('type', DropdownFilter)]
    inlines = [OderFieldsInline]
    search_fields = ['order_number', 'bill__number']

@admin.register(TakeoutOrder)
class TakeoutOrderAdmin(admin.ModelAdmin):
    list_display =[
'order_group',
        'client_name',
'client_phone',
'status',
'cashier',
'sequence',
'created'
    ]
    list_filter = [('status', DropdownFilter), ('cashier__restaurant', RelatedDropdownFilter)]
    search_fields = ['client_name', 'client_phone', 'sequence', 'order_group__order_number']

class PaymentInline(admin.TabularInline):
    model = Payment

class BillsInline(admin.TabularInline):
    model = Bill
    fields = ['number', 'open', 'client_name']
@admin.register(PaymentGroup)
class PaymentGroupAdmin(admin.ModelAdmin):
    list_display = ['type', 'tip', 'total', 'cashier', 'created']
    inlines = [BillsInline,PaymentInline]
    list_filter = [('cashier__restaurant', RelatedDropdownFilter), ('type', DropdownFilter), 'created']


@admin.register(CancelationReason)
class CancelationReasonAdmin(admin.ModelAdmin):
    pass
