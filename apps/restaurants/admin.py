from django.contrib import admin
from .models import ProductComplementItem, Restaurant, Employer, Product, ProductCategory, ProductComplementCategory, RestauratCategory, Table, Catalog, Printer, Sidebar
# Register your models here.
from django_admin_listfilter_dropdown.filters import ChoiceDropdownFilter, RelatedDropdownFilter, DropdownFilter
from django.utils.translation import gettext as _


@admin.register(Restaurant)
class ResstaurantAdmin(admin.ModelAdmin):
    list_display = ['title', 'slug', 'category', 'state', 'city', 'owner', 'open']
    prepopulated_fields = {'slug': ('title',)}
    save_on_top = True
    search_fields = ['title', 'slug', 'state', 'city', 'owner__first_name', 'owner__last_name', 'owner__email']
    list_filter = [('state', ChoiceDropdownFilter), ('category', ChoiceDropdownFilter), ('open',ChoiceDropdownFilter ) ]
    readonly_fields = ['id']
    fieldsets = [
        (_('Restaurant'), {
            'fields': [
                'id',
                'photo',
                'title',
                'slug',
                'email',
                'category',
                'phone',
                'description',
                'open',
                'owner',
            ],
            'classes': [],
        }),
         (_('Adress'), {
            'fields': [
                'zip_code',
                'state',
                'city',
                'street',
                'number',
                'complement',
            ],
            'classes': ('collapse',),
        }),
    ]
    pass

@admin.register(Employer)
class EmployerAdmin(admin.ModelAdmin):
    list_display = ['user', 'office', 'restaurant', 'sallary', 'active']
    search_fields = ['user__first_name', 'user__last_name', 'user__email', 'office', 'restaurant__title']
    list_filter = [('restaurant', ChoiceDropdownFilter), ('office', DropdownFilter), 'sallary']
    pass

class ExtraFieldsInline(admin.TabularInline):
    model = ProductComplementCategory

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['title', 'price', 'product_category', 'active', 'listed', 'order']
    list_editable = ['active', 'listed', 'order']
    search_fields = ['title', 'product_category__title']
    list_filter = [
                    ('product_category__restaurant', RelatedDropdownFilter), 
                    ('product_category', RelatedDropdownFilter), 
                    ('active', ChoiceDropdownFilter), 
                    ('listed', ChoiceDropdownFilter)
                   ]
    save_on_top = True
    inlines = [ExtraFieldsInline,]
    fieldsets = [
        (_('Product'), {
            'fields': [
                'title',
                'description',
                'price',
                'order',
                'active',
                'listed',
                'product_category',
                'type_of_sale',
                'printer',
            ],
            'classes': []
        }),
        (_('Tax Module'), {
            'fields': [
                'codigo_ncm',
                'codigo_produto',
                'valor_unitario_comercial',
                'valor_unitario_tributavel',
                'product_tax_description',
                'unidade_comercial',
                'unidade_tributavel',
                'icms_origem',
                'icms_situacao_tributaria',
                'icms_aliquota',
                'icms_base_calculo',
                'icms_modalidade_base_calculo',
            ],
            'classes': ['collapse']
        }),
    ]
    pass

@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ['title', 'restaurant', 'order']
    list_editable = ['order']
    search_fields = ['title', 'restaurant__title']
    list_filter = [('restaurant', RelatedDropdownFilter)]
    pass

@admin.register(RestauratCategory)
class ProductComplementAdmin(admin.ModelAdmin):
    pass

@admin.register(Table)
class TableAdmin(admin.ModelAdmin):
    list_display = ['title','restaurant', 'capacity','active', 'order']
    list_editable = ['active', 'order']
    list_display_links = ['title', 'restaurant']
    search_fields = ['title'],
    list_filter = [('restaurant', RelatedDropdownFilter), ('active', ChoiceDropdownFilter)]
    pass

@admin.register(Catalog)
class CatalogAdmin(admin.ModelAdmin):
    list_display = ['title', 'restaurant', 'active', 'order']
    list_editable = ['active', 'order']
    list_display_links = ['title', 'restaurant']
    search_fields = ['title'],
    list_filter = [('restaurant', RelatedDropdownFilter), ('active', ChoiceDropdownFilter)]
    filter_horizontal = ['products']
    save_on_top = True
    pass

@admin.register(Printer)
class PrinterAdmin(admin.ModelAdmin):
    pass

class ProductComplementItemInline(admin.TabularInline):
    model = ProductComplementItem

@admin.register(ProductComplementCategory)
class ProductComplementCategoryAdmin(admin.ModelAdmin):
    inlines = [ProductComplementItemInline,]

@admin.register(ProductComplementItem)
class ProductComplementItemAdmin(admin.ModelAdmin):
    pass


@admin.register(Sidebar)
class SidebarAdmin(admin.ModelAdmin):
    pass