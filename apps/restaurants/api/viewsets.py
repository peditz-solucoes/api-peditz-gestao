

from rest_framework import viewsets
from apps.restaurants.models import (
    Restaurant,
    Employer,
    ProductCategory,
    Product,
    ProductComplementCategory,
    ProductComplementItem,
    Table,
)
from .serializers import (
    RestaurantSerializer, 
    EmployerSerializer, 
    ProductCategorySerializer, 
    ProductSerializer,
    ProductComplementSerializer,
    ProductComplementItemSerializer,
    TableSerializer,
    UserPermissionsSerializer,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django_filters.rest_framework import DjangoFilterBackend



class RestaurantViewSet(viewsets.ModelViewSet):
    queryset = Restaurant.objects.all()
    serializer_class = RestaurantSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Restaurant.objects.all() 
        return Restaurant.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

class EmployerViewSet(viewsets.ModelViewSet):
    serializer_class = EmployerSerializer
    permission_classes = (IsAuthenticated,)
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_queryset(self):
        user = self.request.user
        if user.restaurants:
            return user.restaurants.employers.all()
        if user.employer is not None:
            return Employer.objects.filter(user=user)
        return Employer.objects.none()
    
    def create(self, request, *args, **kwargs):
        if not Restaurant.objects.filter(owner=request.user).exists():
            return Response({"detail": "You must be an owner of a restaurant to create an employer."}, status=status.HTTP_403_FORBIDDEN)

        return super().create(request, *args, **kwargs)
    
class ProductCategoryViewSet(viewsets.ModelViewSet):
    serializer_class = ProductCategorySerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return ProductCategory.objects.filter(restaurant__owner=self.request.user) 

    def perform_create(self, serializer):
        serializer.save(restaurant=self.request.user.restaurants)

class ProductViewSet(viewsets.ModelViewSet):
    serializer_class = ProductSerializer
    permission_classes = (IsAuthenticated,)
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['product_category', 'active', 'listed','printer', 'title']
    def get_queryset(self):
        user = self.request.user
        if user.employer is not None:
            return  Product.objects.filter(product_category__restaurant=user.employer.restaurant)
        if user.restaurants:
            return  Product.objects.filter(product_category__restaurant=user.restaurants)
        return Product.objects.none()

class ProductComplentViewSet(viewsets.ModelViewSet):
    serializer_class = ProductComplementSerializer
    permission_classes = (IsAuthenticated,)
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['product', 'active']
    def get_queryset(self):
        return  ProductComplementCategory.objects.filter()
    
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
        if user.employer is not None:
            return  Table.objects.filter(restaurant=user.employer.restaurant)
        if user.restaurants:
            return  Table.objects.filter(restaurant=user.restaurants)
        return Table.objects.none()
    
class UserPermissionViewSet(viewsets.ModelViewSet):
    serializer_class = UserPermissionsSerializer
    permission_classes = (IsAuthenticated,)
    def get_queryset(self):
        return  Employer.objects.filter(user=self.request.user)
    http_method_names = ['get']