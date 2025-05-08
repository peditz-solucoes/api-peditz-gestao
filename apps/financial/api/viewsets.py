

from rest_framework import viewsets
from rest_framework.response import Response
from apps.financial.models import (
    Cashier,
    Bill,
    OrderGroup,
    PaymentMethod,
    PaymentGroup,
    OrderStatus
)
from apps.restaurants.models import Employer
from .serializers import (
    CashierSerializer,
    BillSerializer,
    ListPaymentsGroupsSerializer,
    OrderGroupSerialier,
    OrderGroupListSerializer,
    DeleteOrderSerializer,
    PaymentsMethodSerializer,
    PaymentGroupSerializer,
    CloseBillSerializer,
    TakeOutOurderSerialier,
    OrderStatusSerializer,
    DeliveryOrderSerialier,
    CashierStatsSerializer
)
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django_filters import rest_framework as filters



class CashierViewSet(viewsets.ModelViewSet):
    queryset = Cashier.objects.all()
    serializer_class = CashierSerializer
    permission_classes = (IsAuthenticated,)
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['open', 'opened_by', 'closed_by']
    
    def get_queryset(self):
        user = self.request.user
        try: 
            return Cashier.objects.filter(restaurant=user.employer.restaurant)
        except AttributeError:
            if user.restaurants:
                return Cashier.objects.filter(restaurant=user.restaurants)
        return Cashier.objects.none()
    
class BillViewSet(viewsets.ModelViewSet):
    serializer_class = BillSerializer
    permission_classes = (IsAuthenticated,)
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['cashier', 'open', 'number', 'opened_by']
    http_method_names = ['get', 'post']

    def get_queryset(self):
        user = self.request.user
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
class TakeOutOurderViewSet(viewsets.ModelViewSet):
    serializer_class = TakeOutOurderSerialier
    permission_classes = (IsAuthenticated,)
    queryset = OrderGroup.objects.all().order_by('created')
    http_method_names = ['post']

    def get_queryset(self):
        user = self.request.user
        try:
            restaurant = user.employer.restaurant
            return OrderGroup.objects.filter(restaurant=restaurant)
        except AttributeError:
            return OrderGroup.objects.none()
class DeliveryOrderViewSet(viewsets.ModelViewSet):
    serializer_class = DeliveryOrderSerialier
    # permission_classes = (IsAuthenticated,)
    queryset = OrderGroup.objects.all().order_by('created')
    http_method_names = ['post']

    def get_queryset(self):
        user = self.request.user
        try:
            restaurant = user.employer.restaurant
            return OrderGroup.objects.filter(restaurant=restaurant)
        except AttributeError:
            return OrderGroup.objects.none()
    
class OrderGroupListViewSet(viewsets.ModelViewSet):
    serializer_class = OrderGroupListSerializer
    permission_classes = (IsAuthenticated,)
    http_method_names = ['get']
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['type', 'bill', 'collaborator', 'status', 'bill__cashier', 'takeout_order__cashier', 'cashier']

    def get_queryset(self):
        user = self.request.user
        try:
            restaurant = user.employer.restaurant
            return OrderGroup.objects.filter(restaurant=restaurant)
        except AttributeError:
            try:
                restaurant = user.restaurants
                return OrderGroup.objects.filter(restaurant=restaurant)
            except AttributeError:
                return OrderGroup.objects.none()

class DeleteOrderViewSet(viewsets.ModelViewSet):
    serializer_class = DeleteOrderSerializer
    permission_classes = (IsAuthenticated,)
    http_method_names = ['post']

    def get_queryset(self):
        return OrderGroup.objects.none()
    
class PaymentMethodViewSet(viewsets.ModelViewSet):
    serializer_class = PaymentsMethodSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        user = self.request.user
        try:
            restaurant = user.employer.restaurant
            return PaymentMethod.objects.filter(restaurant=restaurant)
        except AttributeError:
            try:
                restaurant = user.restaurants
                return PaymentMethod.objects.filter(restaurant=restaurant)
            except AttributeError:
                return PaymentMethod.objects.none()


class PaymentGroupViewSet(viewsets.ModelViewSet):
    serializer_class = PaymentGroupSerializer
    permission_classes = (IsAuthenticated,)
    http_method_names = ['post']

    def get_queryset(self):
        user = self.request.user
        try:
            restaurant = user.employer.restaurant
            return PaymentGroup.objects.filter(cashier__restaurant=restaurant)
        except AttributeError:
            try:
                restaurant = user.restaurants
                return PaymentGroup.objects.filter(cashier__restaurant=restaurant)
            except AttributeError:
                return PaymentGroup.objects.none()
            

class PaymentGroupFilter(filters.FilterSet):
    datetime_range = filters.DateTimeFromToRangeFilter(field_name='created')

    class Meta:
        model = PaymentGroup
        fields = ['cashier', 'type', 'datetime_range']
            
class ListPaymentGroupViewSet(viewsets.ModelViewSet):
    serializer_class = ListPaymentsGroupsSerializer
    permission_classes = (IsAuthenticated,)
    http_method_names = ['get']
    filter_backends = [DjangoFilterBackend]
    filterset_class = PaymentGroupFilter
    
    def get_queryset(self):
        user = self.request.user
        try:
            employer = Employer.objects.get(user=user)
        except Employer.DoesNotExist:
            return PaymentGroup.objects.none()
        try:
            restaurant = user.employer.restaurant
            if employer.role == 'GERENTE' or employer.office == 'Caixa':
                return PaymentGroup.objects.filter(cashier__restaurant=restaurant)
            else:
                return PaymentGroup.objects.none()
        except AttributeError:
            try:
                restaurant = user.restaurants
                if employer.role == 'GERENTE' or employer.office == 'Caixa':
                    return PaymentGroup.objects.filter(cashier__restaurant=restaurant)
                else:
                    return PaymentGroup.objects.none()
            except AttributeError:
                return PaymentGroup.objects.none()
            
class CloseBillViewSet(viewsets.ModelViewSet):
    serializer_class = CloseBillSerializer
    permission_classes = (IsAuthenticated,)
    http_method_names = ['post']

    def get_queryset(self):
        return Bill.objects.none()
    

class OrderStatusViewSet(viewsets.ModelViewSet):
    serializer_class = OrderStatusSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        user = self.request.user
        if user.employer is not None:
            restaurant = user.employer.restaurant
            return OrderStatus.objects.filter(restaurant=restaurant)
        return OrderGroup.objects.none()
    

class CashierStatsViewSet(viewsets.ModelViewSet):
    serializer_class = CashierStatsSerializer
    permission_classes = (IsAuthenticated,)
    http_method_names = ['get']
    def get_queryset(self):
        return Cashier.objects.all()