

from rest_framework import viewsets
from apps.financial.models import (
    Cashier,
    Bill,
)
from apps.restaurants.models import (
    Employer,
    Restaurant,
)
from .serializers import (
    CashierSerializer,
    BillSerializer,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django_filters.rest_framework import DjangoFilterBackend



class CashierViewSet(viewsets.ModelViewSet):
    queryset = Cashier.objects.all()
    serializer_class = CashierSerializer
    permission_classes = (IsAuthenticated,)
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['open', 'opened_by', 'closed_by']
    
    def get_queryset(self):
        user = self.request.user
        try:
            restaurant = Restaurant.objects.get(owner=user)
        except Restaurant.DoesNotExist:
            restaurant = None
            try:
                employer = Employer.objects.get(user=user)
                restaurant = employer.restaurant
            except Employer.DoesNotExist:
                return Cashier.objects.none()
        
        return Cashier.objects.filter(restaurant=restaurant)
    
class BillViewSet(viewsets.ModelViewSet):
    serializer_class = BillSerializer
    permission_classes = (IsAuthenticated,)
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['cashier', 'open', 'number', 'opened_by']
    http_method_names = ['get', 'post']

    def get_queryset(self):
        user = self.request.user
        try:
            restaurant = Restaurant.objects.get(owner=user)
        except Restaurant.DoesNotExist:
            restaurant = None
            try:
                employer = Employer.objects.get(user=user)
                restaurant = employer.restaurant
            except Employer.DoesNotExist:
                return Bill.objects.none()
        
        return Bill.objects.filter(cashier__restaurant=restaurant)