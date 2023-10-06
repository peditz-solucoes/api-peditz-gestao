from rest_framework import viewsets

from .serializers import ItemCategorySerializer, ItemSerializer
from ..models import Item, ItemCategory
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
