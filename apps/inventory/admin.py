from django.contrib import admin
from .models import Item, ItemCategory, ItemTransaction, ProductItem, ItemItem
# Register your models here.

class ItemItemInline(admin.TabularInline):
    model = ItemItem
    fk_name = 'item'
    extra = 0

class ProductItemInline(admin.TabularInline):

    model = ProductItem
    extra = 0

@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    inlines = [
        ItemItemInline,
        ProductItemInline
    ]

@admin.register(ItemCategory)
class ItemCategoryAdmin(admin.ModelAdmin):
    pass

@admin.register(ItemTransaction)
class ItemTransactionAdmin(admin.ModelAdmin):
    pass

@admin.register(ProductItem)
class ProductItemAdmin(admin.ModelAdmin):
    pass

@admin.register(ItemItem)
class ItemItemAdmin(admin.ModelAdmin):
    pass    



