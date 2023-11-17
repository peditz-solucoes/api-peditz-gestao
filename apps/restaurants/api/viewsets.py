

from rest_framework import viewsets
from apps.restaurants.models import (
    Printer,
    ProductPrice,
    Restaurant,
    Employer,
    ProductCategory,
    Product,
    ProductComplementCategory,
    ProductComplementItem,
    Sidebar,
    Table,
    Catalog
)
from rest_framework.exceptions import PermissionDenied

from apps.financial.models import (
    Order,
)
from peditz.stats import StatsApi
from .serializers import (
    CatalogCrudSerializer,
    CatalogSerializer,
    PrinterSerializer,
    ProductCatalogSerializer,
    ProductPriceSerializer,
    ProductsStatsSerializer,
    RestaurantCatalogSerializer,
    RestaurantSerializer, 
    EmployerSerializer, 
    ProductCategorySerializer, 
    ProductSerializer,
    ProductComplementSerializer,
    ProductComplementItemSerializer,
    SidebarSerializer,
    TableSerializer,
    UserPermissionsSerializer,
)
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework import status
from django_filters.rest_framework import DjangoFilterBackend
from django_filters import rest_framework as filters

stats_api = StatsApi()

class RestaurantViewSet(viewsets.ModelViewSet):
    queryset = Restaurant.objects.all()
    serializer_class = RestaurantSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        user = self.request.user
        if user.employer is not None:
            return Restaurant.objects.filter(id=user.employer.restaurant.id)
        return Restaurant.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

class EmployerViewSet(viewsets.ModelViewSet):
    serializer_class = EmployerSerializer
    permission_classes = (IsAuthenticated,)
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_queryset(self):
        user = self.request.user
        if user.employer.role == 'GERENTE':
            restaurant = user.employer.restaurant
            return Employer.objects.filter(restaurant=restaurant)
        return Employer.objects.none()
    
    def create(self, request, *args, **kwargs):
        if request.user.employer.role != 'GERENTE':
            return Response({"detail": "Você não tem permissão para adicionar funcionário"}, status=status.HTTP_403_FORBIDDEN)
        return super().create(request, *args, **kwargs)
    
class ProductCategoryViewSet(viewsets.ModelViewSet):
    serializer_class = ProductCategorySerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        user = self.request.user
        try:
            return ProductCategory.objects.filter(restaurant=user.employer.restaurant)
        except AttributeError:
            try:
                return ProductCategory.objects.filter(restaurant=user.restaurants)
            except AttributeError:
                return ProductCategory.objects.none()

    def perform_create(self, serializer):
        serializer.save(restaurant=self.request.user.restaurants)

class ProductViewSet(viewsets.ModelViewSet):
    serializer_class = ProductSerializer
    permission_classes = (IsAuthenticated,)
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['product_category', 'active', 'listed','printer', 'title']
    def get_queryset(self):
        user = self.request.user
        try:
            return  Product.objects.filter(product_category__restaurant=user.employer.restaurant).order_by('product_category__order', 'product_category__title','order', 'title')
        except AttributeError:
            try:
                return  Product.objects.filter(product_category__restaurant=user.restaurants).order_by('product_category__order', 'product_category__title','order', 'title')
            except AttributeError:
                return Product.objects.none()

class ProductComplentViewSet(viewsets.ModelViewSet):
    serializer_class = ProductComplementSerializer
    permission_classes = (IsAuthenticated,)
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['products', 'active']
    def get_queryset(self):
        user = self.request.user
        try:
            return  ProductComplementCategory.objects.filter(restaurant=user.employer.restaurant).order_by('order')
        except AttributeError:
            try:
                return  ProductComplementCategory.objects.filter(restaurant=user.restaurants).order_by('order')
            except AttributeError:
                return ProductComplementCategory.objects.none()
    
class ProductComplentItemViewSet(viewsets.ModelViewSet):
    serializer_class = ProductComplementItemSerializer
    permission_classes = (IsAuthenticated,)
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['title']
    def get_queryset(self):
        return  ProductComplementItem.objects.filter()
    
class TableViewSet(viewsets.ModelViewSet):
    serializer_class = TableSerializer
    permission_classes = (IsAuthenticated,)
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['active']
    def get_queryset(self):
        user = self.request.user
        try:
            return  Table.objects.filter(restaurant=user.employer.restaurant)
        except AttributeError:
            try:
                return  Table.objects.filter(restaurant=user.restaurants)
            except AttributeError:                
                return Table.objects.none()
    
class UserPermissionViewSet(viewsets.ModelViewSet):
    serializer_class = UserPermissionsSerializer
    permission_classes = (IsAuthenticated,)
    def get_queryset(self):
        return  Employer.objects.filter(user=self.request.user)
    http_method_names = ['get']

class PrinterViewSet(viewsets.ModelViewSet):
    serializer_class = PrinterSerializer
    permission_classes = (IsAuthenticated,)
    def get_queryset(self):
        user = self.request.user
        try:
            employer = user.employer
            return  Printer.objects.filter(restaurant=employer.restaurant)
        except AttributeError:
            try: 
                restaurant = user.restaurants
                return  Printer.objects.filter(restaurant=restaurant)
            except AttributeError:
                return Printer.objects.none()
            
class ProductCatalogViewSet(viewsets.ModelViewSet):
    serializer_class = ProductCatalogSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    http_method_names = ['get']
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['listed',]

    def get_queryset(self):
        return Product.objects.filter(active=True, product_category__active=True, product_category__restaurant__active=True).order_by('product_category__order', 'product_category__title','order', 'title')

class CatalogViewSet(viewsets.ModelViewSet):
    serializer_class = CatalogSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    http_method_names = ['get']
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['slug', 'restaurant__slug']

    def get_queryset(self):
        return Catalog.objects.filter(active=True).order_by('order', 'title')
    
class RestaurantCatalogViewSet(viewsets.ModelViewSet):
    serializer_class = RestaurantCatalogSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    http_method_names = ['get']
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['slug',]

    def get_queryset(self):
        return Restaurant.objects.filter(active=True)
    
class SidebartViewSet(viewsets.ModelViewSet):
    serializer_class = SidebarSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    http_method_names = ['get']

    def get_queryset(self):
        return Sidebar.objects.all()
    
class ProductPriceViewSet(viewsets.ModelViewSet):
    serializer_class = ProductPriceSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    http_method_names = ['get', 'post', 'patch', 'delete']
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['product']

    def get_queryset(self):
        user = self.request.user
        try:
            return  ProductPrice.objects.filter(product__product_category__restaurant=user.employer.restaurant).order_by('product__product_category__title','product__order', 'product__title')
        except AttributeError:
            try:
                return  ProductPrice.objects.filter(product__product_category__restaurant=user.restaurants).order_by('product__product_category__title', 'product__order', 'product__title')
            except AttributeError:
                return Product.objects.none()
class CatalogCrudViewSet(viewsets.ModelViewSet):
    serializer_class = CatalogCrudSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    http_method_names = ['get', 'post', 'patch', 'delete']
    filter_backends = [DjangoFilterBackend]
    # filterset_fields = ['']

    def get_queryset(self):
        user = self.request.user
        try:
            return  Catalog.objects.filter(restaurant=user.employer.restaurant).order_by('order','created')
        except AttributeError:
            try:
                return  Catalog.objects.filter(restaurant=user.restaurants).order_by('order', 'created')
            except AttributeError:
                return Product.objects.none()


class ProductsStatsFilter(filters.FilterSet):
    initial_date = filters.DateFilter(field_name='created', lookup_expr='gte')
    final_date = filters.DateFilter(field_name='created', lookup_expr='lte')

    class Meta:
        model = Order
        fields = ['initial_date', 'final_date']
            

class ProductsStatsViewSet(viewsets.ModelViewSet):
    serializer_class = ProductsStatsSerializer
    http_method_names = ['get']
    permmision_classes = (IsAuthenticated,)
    filter_backends = [DjangoFilterBackend]

    def get_queryset(self):
        try:
            user = self.request.user
            restaurant = user.employer.restaurant
        except AttributeError:
            try:
                restaurant = user.restaurants
            except AttributeError:
                raise PermissionDenied(detail="Você não tem permissão para acessar essas informações")
        
        response = stats_api.get_products_stats(
            restaurant_id=restaurant.id,
            initial_date=self.request.GET.get('initialDate'),
            final_date=self.request.GET.get('finalDate'),
            category_id=self.request.GET.get('categoryId') or '',
        )
        return response


