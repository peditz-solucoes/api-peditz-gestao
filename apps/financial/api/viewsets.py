

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
        if user.employer:
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
        if user.employer:
            return Bill.objects.filter(cashier__restaurant=user.employer.restaurant)
        return Bill.objects.none()
    
class OrderGroupViewSet(viewsets.ModelViewSet):
    serializer_class = OrderGroupSerialier
    permission_classes = (IsAuthenticated,)
    queryset = OrderGroup.objects.all().order_by('created')

    def get_queryset(self):
        user = self.request.user
        if user.employer:
            restaurant = user.employer.restaurant
            return OrderGroup.objects.filter(restaurant=restaurant)
        return OrderGroup.objects.none()
