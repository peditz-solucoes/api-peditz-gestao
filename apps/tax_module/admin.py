from django.contrib import admin
from .models import Company, Tax, PaymentItemsMethods, TaxItems
# Register your models here.


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    pass

@admin.register(Tax)
class TaxAdmin(admin.ModelAdmin):
    pass

@admin.register(PaymentItemsMethods)
class PaymentItemsMethodsAdmin(admin.ModelAdmin):
    pass

@admin.register(TaxItems)
class TaxItemsAdmin(admin.ModelAdmin):
    pass

