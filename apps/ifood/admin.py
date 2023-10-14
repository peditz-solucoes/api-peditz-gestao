from django.contrib import admin

from apps.ifood.models import IfoodUserCredentials

# Register your models here.

@admin.register(IfoodUserCredentials)
class IfoodUserCredentialsAdmin(admin.ModelAdmin):
    pass