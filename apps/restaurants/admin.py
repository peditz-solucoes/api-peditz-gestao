from django.contrib import admin
from .models import Restaurant, Employer, Product, ProductCategory, ProductComplement, RestauratCategory, Table
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
    fieldsets = [
        (_('Restaurant'), {
            'fields': [
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
    model = ProductComplement

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
            ],
            'classes': []
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
