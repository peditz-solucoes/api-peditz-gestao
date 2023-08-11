

from rest_framework import viewsets
from apps.financial.models import (
    Cashier,
    Bill,
    OrderGroup,
)
from .serializers import (
    CashierSerializer,
    BillSerializer,
    OrderGroupSerialier,
    OrderGroupListSerializer,
)
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend



class CashierViewSet(viewsets.ModelViewSet):
    queryset = Cashier.objects.all()
    serializer_class = CashierSerializer
    permission_classes = (IsAuthenticated,)
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['open', 'opened_by', 'closed_by']
    
    def get_queryset(self):
        user = self.request.user
        if user.restaurants:
            return Cashier.objects.filter(restaurant=user.restaurants)
        if user.employer is not None:
            return Cashier.objects.filter(restaurant=user.employer.restaurant)
        return Cashier.objects.none()
    
class BillViewSet(viewsets.ModelViewSet):
    serializer_class = BillSerializer
    permission_classes = (IsAuthenticated,)
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['cashier', 'open', 'number', 'opened_by']
    http_method_names = ['get', 'post']

    def get_queryset(self):
        user = self.request.user
        if user.restaurants:
            return Bill.objects.filter(cashier__restaurant=user.restaurants)
        if user.employer is not None: 
            return Bill.objects.filter(cashier__restaurant=user.employer.restaurant)
        return Bill.objects.none()
    
class OrderGroupViewSet(viewsets.ModelViewSet):
    serializer_class = OrderGroupSerialier
    permission_classes = (IsAuthenticated,)
    queryset = OrderGroup.objects.all().order_by('created')
    http_method_names = ['post']

    def get_queryset(self):
        user = self.request.user
        if user.employer is not None:
            restaurant = user.employer.restaurant
            return OrderGroup.objects.filter(restaurant=restaurant)
        return OrderGroup.objects.none()
    
class OrderGroupListViewSet(viewsets.ModelViewSet):
    serializer_class = OrderGroupListSerializer
    permission_classes = (IsAuthenticated,)
    http_method_names = ['get']
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['bill', 'collaborator', 'status', 'bill__cashier']

    def get_queryset(self):
        user = self.request.user
        if user.employer is not None:
            restaurant = user.employer.restaurant
            return OrderGroup.objects.filter(restaurant=restaurant)
        return OrderGroup.objects.none()
