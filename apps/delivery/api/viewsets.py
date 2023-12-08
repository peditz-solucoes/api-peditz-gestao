from rest_framework import viewsets

from ..models import Client, ClientAdress, DeliveryOrder, DeliveryRestaurantConfig, DeliveryStatus
from .serializers import ClientSerializer, ClientAdressSerializer, PaymentMethodsSerializer, OrderSerializer, DeliveryConfigSerializer, DeliveryStatusSerializer, PaymentDelveryserializer
from apps.financial.models import PaymentMethod, PaymentGroup
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import IsAuthenticated

from django_filters import rest_framework as filters
class ClientViewSet(viewsets.ModelViewSet):
    serializer_class = ClientSerializer
    queryset = Client.objects.all()
    http_method_names = ['post', 'get']

class ClientAdressViewSet(viewsets.ModelViewSet):
    serializer_class = ClientAdressSerializer
    queryset = ClientAdress.objects.all()
    http_method_names = ['post', 'get']

class PaymentMethodsDeliveryViewSet(viewsets.ModelViewSet):
    serializer_class = PaymentMethodsSerializer
    queryset = PaymentMethod.objects.filter(active=True, acept_on_delivery=True)
    http_method_names = ['get']
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['restaurant']

class DeliveryViewsets(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    queryset = DeliveryOrder.objects.all()
    http_method_names = ['get']

class DeliveryRestaurantViewsets(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    queryset = DeliveryOrder.objects.all()
    http_method_names = ['get']
    filter_backends = [DjangoFilterBackend]
    permission_classes = (IsAuthenticated,)
    filterset_fields = ['order_group__cashier']


    def get_queryset(self):
        user = self.request.user
        try:
            restaurant = user.employer.restaurant
            return DeliveryOrder.objects.filter(order_group__restaurant=restaurant)
        except AttributeError:
            return DeliveryOrder.objects.none()

class DeliveryConfigsViewSet(viewsets.ModelViewSet):
    serializer_class = DeliveryConfigSerializer
    queryset = DeliveryRestaurantConfig.objects.all()
    http_method_names = ['get', 'post', 'put', 'patch']
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['restaurant']


class DeliveryStatusViewSet(viewsets.ModelViewSet):
    serializer_class = DeliveryStatusSerializer
    queryset = DeliveryStatus.objects.all()
    http_method_names = ['get', 'post']
    permission_classes = (IsAuthenticated,)


    def get_queryset(self):
        user = self.request.user
        try:
            restaurant = user.employer.restaurant
            return DeliveryStatus.objects.filter(order__order_group__restaurant=restaurant)
        except AttributeError:
            return DeliveryOrder.objects.none()
        
class PaymentDelverysViewSet(viewsets.ModelViewSet):
    serializer_class = PaymentDelveryserializer
    queryset = PaymentGroup.objects.all()
    http_method_names = ['get', 'post']

    permission_classes = (IsAuthenticated,)