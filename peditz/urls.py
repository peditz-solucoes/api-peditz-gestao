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
    ProductComplentItemViewSet, 
    RestaurantViewSet, 
    EmployerViewSet, 
    ProductCategoryViewSet, 
    ProductViewSet, 
    ProductComplentViewSet,
    TableViewSet
)

from drf_yasg.views import get_schema_view
from drf_yasg import openapi



admin.sites.AdminSite.site_header = 'Adiministração Peditz'
admin.sites.AdminSite.site_title = 'Peditz Gestão'
admin.sites.AdminSite.index_title = 'Peditz Gestão'


router = routers.DefaultRouter()

router.register(r'restaurant', RestaurantViewSet, basename='restaurant') 
router.register(r'employer', EmployerViewSet, basename='employer') 
router.register(r'product-category', ProductCategoryViewSet, basename='product-category') 
router.register(r'product', ProductViewSet, basename='product') 
router.register(r'product-complement', ProductComplentViewSet, basename='product-complement')
router.register(r'product-complement-item', ProductComplentItemViewSet, basename='product-complement-item')
router.register(r'tables', TableViewSet, basename='tables')

schema_view = get_schema_view(
    openapi.Info(
        title='API Peditz Gestão',
        default_version='0.0.1',
        description='API para gestão de restaurantes',
    )
)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include(router.urls)),
    path('api/v1/', include('rest_framework.urls')),
    path('api/v1/auth/registration/', include('dj_rest_auth.registration.urls')),
    path('api/v1/auth/', include('dj_rest_auth.urls')),
    path('api/v1/account/', include('allauth.urls')),
    path('api/v1/docs/', schema_view.with_ui('swagger', cache_timeout=0), name='api_docs'),

]
