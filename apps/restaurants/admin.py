from django.contrib import admin
from .models import Restaurant, Employer, Product, ProductCategory, ProductComplement
# Register your models here.


@admin.register(Restaurant)
class ResstaurantAdmin(admin.ModelAdmin):
    pass

@admin.register(Employer)
class EmployerAdmin(admin.ModelAdmin):
    pass

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    pass

@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    pass

@admin.register(ProductComplement)
class ProductComplementAdmin(admin.ModelAdmin):
    pass