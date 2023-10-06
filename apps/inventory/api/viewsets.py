from rest_framework import viewsets

from .serializers import ItemCategorySerializer, ItemIngredientSerializer, ItemSerializer, ItemStockTransactionSerializer
from ..models import Item, ItemCategory, ItemItem, ItemTransaction
from django_filters.rest_framework import DjangoFilterBackend

class ItemStockViewSet(viewsets.ModelViewSet):
    serializer_class = ItemSerializer
    queryset = Item.objects.all()

    def get_queryset(self):
        user = self.request.user
        try:
            return Item.objects.filter(category__restaurant=user.employer.restaurant).order_by('created')
        except AttributeError:
            return Item.objects.none()
    
class ItemStockCategoryViewSet(viewsets.ModelViewSet):
    serializer_class = ItemCategorySerializer
    queryset = ItemCategory.objects.all()

    def get_queryset(self):
        user = self.request.user
        try:
            return ItemCategory.objects.filter(restaurant=user.employer.restaurant).order_by('created')
        except AttributeError:
            return ItemCategory.objects.none()
        
class ItemStockTransactionViewSet(viewsets.ModelViewSet):
    serializer_class = ItemStockTransactionSerializer
    queryset = ItemTransaction.objects.all()
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['item']

    def get_queryset(self):
        user = self.request.user
        try:
            return ItemTransaction.objects.filter(item__category__restaurant=user.employer.restaurant).order_by('created')
        except AttributeError:
            return ItemTransaction.objects.none()
        
class ItemIngredientViewSet(viewsets.ModelViewSet):
    serializer_class = ItemIngredientSerializer
    queryset = ItemItem.objects.all()
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['item', 'ingredient']

    def get_queryset(self):
        user = self.request.user
        try:
            return ItemItem.objects.filter(item__category__restaurant=user.employer.restaurant, ingredient__category__restaurant=user.employer.restaurant).order_by('created')
        except AttributeError:
            return ItemItem.objects.none()