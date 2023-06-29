from django.contrib import admin
from .models import Item, ItemCategory, ItemTransaction
# Register your models here.

@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    pass

@admin.register(ItemCategory)
class ItemCategoryAdmin(admin.ModelAdmin):
    pass

@admin.register(ItemTransaction)
class ItemTransactionAdmin(admin.ModelAdmin):
    pass