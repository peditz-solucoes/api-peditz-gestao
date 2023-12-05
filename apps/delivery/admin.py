from django.contrib import admin

# Register your models here.

from .models import (
    Client,
    ClientAdress,
    DeliveryOrder,
    DeliveryRestaurantConfig,
    DeliveryStatus,
)

class ClientAdressInline(admin.TabularInline):
    model = ClientAdress


class DeliveryStatusInline(admin.TabularInline):
    model = DeliveryStatus


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    inlines = [ClientAdressInline]

@admin.register(ClientAdress)
class ClientAdressAdmin(admin.ModelAdmin):
    pass

@admin.register(DeliveryOrder)
class DeliveryOrderAdmin(admin.ModelAdmin):
    inlines = [DeliveryStatusInline]

@admin.register(DeliveryRestaurantConfig)
class DeliveryRestaurantConfigAdmin(admin.ModelAdmin):
    pass
