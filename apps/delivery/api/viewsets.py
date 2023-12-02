from rest_framework import viewsets

from ..models import Client, ClientAdress
from .serializers import ClientSerializer, ClientAdressSerializer, PaymentMethodsSerializer
from apps.financial.models import PaymentMethod
from django_filters.rest_framework import DjangoFilterBackend
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
    queryset = PaymentMethod.objects.filter(active=True)
    http_method_names = ['get']
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['restaurant']