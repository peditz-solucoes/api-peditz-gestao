"""peditz URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include,path
from rest_framework import routers
from apps.restaurants.api.viewsets import (
    CatalogViewSet,
    PrinterViewSet,
    ProductCatalogViewSet,
    ProductComplentItemViewSet,
    RestaurantCatalogViewSet, 
    RestaurantViewSet, 
    EmployerViewSet, 
    ProductCategoryViewSet, 
    ProductViewSet, 
    ProductComplentViewSet,
    TableViewSet,
    UserPermissionViewSet,
    SidebartViewSet,
    ProductPriceViewSet,
    CatalogCrudViewSet
)
from apps.financial.api.viewsets import (
    CashierViewSet,
    BillViewSet,
    ListPaymentGroupViewSet,
    OrderGroupViewSet,
    OrderGroupListViewSet,
    DeleteOrderViewSet,
    PaymentMethodViewSet,
    PaymentGroupViewSet,
    CloseBillViewSet,
    TakeOutOurderViewSet
)
from apps.inventory.api.viewsets import (
    ItemStockViewSet,
    ItemStockCategoryViewSet,
    ItemStockTransactionViewSet,
    ItemIngredientViewSet,
    ProductItemStockViewset
)

import os
from apps.ifood.api.viewsets import IfoodAuthCodeViewSet, IfoodAuthTokenViewSet, IfoodMerchantsViewSet

from apps.tax_module.api.viewsets import TaxViewSet, TestTaxViewSet, NotesViewSet

# 'Adiministração Peditz'
admin.sites.AdminSite.site_header = os.environ.get('ENVIRONMENT_HEADER', 'Local Adiministração Peditz')
admin.sites.AdminSite.site_title = os.environ.get('ENVIRONMENT_NAME', 'Local Peditz Gestão')
admin.sites.AdminSite.index_title = os.environ.get('ENVIRONMENT_NAME', 'Local Peditz Gestão')


router = routers.DefaultRouter()

router.register(r'restaurant', RestaurantViewSet, basename='restaurant') 
router.register(r'employer', EmployerViewSet, basename='employer') 
router.register(r'product-category', ProductCategoryViewSet, basename='product-category') 
router.register(r'product', ProductViewSet, basename='product') 
router.register(r'product-complement', ProductComplentViewSet, basename='product-complement')
router.register(r'product-complement-item', ProductComplentItemViewSet, basename='product-complement-item')
router.register(r'tables', TableViewSet, basename='tables')
router.register(r'cashier', CashierViewSet, basename='cashier')
router.register(r'bill', BillViewSet, basename='bill')
router.register(r'user-permissions', UserPermissionViewSet, basename='user-permissions')
router.register(r'order', OrderGroupViewSet, basename='order')
router.register(r'order-list', OrderGroupListViewSet, basename='order-list')
router.register(r'order-delete', DeleteOrderViewSet, basename='order-delete')
router.register(r'payment-method', PaymentMethodViewSet, basename='payment-method')
router.register(r'payment', PaymentGroupViewSet, basename='payment')
router.register(r'list-payment', ListPaymentGroupViewSet, basename='list-payment')
router.register(r'print', PrinterViewSet, basename='print')
router.register(r'tax', TaxViewSet, basename='tax')
router.register(r'tax-test', TestTaxViewSet, basename='tax-test')
router.register(r'catalog', CatalogViewSet, basename='catalog')
router.register(r'restaurant-profile', RestaurantCatalogViewSet, basename='restaurant-profile')
router.register(r'close-bill', CloseBillViewSet, basename='close-bill')
router.register(r'sidebar', SidebartViewSet, basename='sidebar')
router.register(r'product-price', ProductPriceViewSet, basename='product-price')
router.register(r'catalog-crud', CatalogCrudViewSet, basename='catalog-crud')
router.register(r'notes', NotesViewSet, basename='notes')
router.register(r'item-stock', ItemStockViewSet, basename='item-stock')
router.register(r'item-stock-category', ItemStockCategoryViewSet, basename='item-stock-category')
router.register(r'item-stock-transaction', ItemStockTransactionViewSet, basename='item-stock-transaction')
router.register(r'item-ingredient', ItemIngredientViewSet, basename='item-ingredient')
router.register(r'product-item-stock', ProductItemStockViewset, basename='product-item-stock-transaction')
router.register(r'take-out', TakeOutOurderViewSet, basename='take-out')
router.register(r'ifood-auth-code', IfoodAuthCodeViewSet, basename='ifood-auth-code')
router.register(r'ifood-auth-token', IfoodAuthTokenViewSet, basename='ifood-auth-token')
router.register(r'ifood-merchants', IfoodMerchantsViewSet, basename='ifood-merchants')


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include(router.urls)),
    path('api/v1/', include('rest_framework.urls')),
    path('api/v1/auth/registration/', include('dj_rest_auth.registration.urls')),
    path('api/v1/auth/', include('dj_rest_auth.urls')),
    path('api/v1/account/', include('allauth.urls')),
]
