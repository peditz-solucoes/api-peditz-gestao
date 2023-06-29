from django.contrib import admin
from .models import Cashier, Bill, Order, PaymentMethod, Payment
# Register your models here.


class OderFieldsInline(admin.TabularInline):
    model = Order
    readonly_fields = ['unit_price',  'total', 'product_title']

@admin.register(Cashier)
class CashierAdmin(admin.ModelAdmin):
    pass

@admin.register(Bill)
class BillAdmin(admin.ModelAdmin):
    inlines = [OderFieldsInline]
    pass

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    pass

@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    pass

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    pass