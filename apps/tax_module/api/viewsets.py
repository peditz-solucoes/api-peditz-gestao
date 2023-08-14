from rest_framework import viewsets

from .serializers import  TaxSerializer, TestTaxSerializer
from ..models import Tax

class TaxViewSet(viewsets.ModelViewSet):
    serializer_class = TaxSerializer
    queryset = Tax.objects.all()
    http_method_names = ['post']

class TestTaxViewSet(viewsets.ModelViewSet):
    serializer_class = TestTaxSerializer
    queryset = Tax.objects.all()
    http_method_names = ['post']
