from rest_framework import viewsets

from .serializers import  NotesSerializer, TaxSerializer, TestTaxSerializer
from ..models import Company, Tax
from django_filters.rest_framework import DjangoFilterBackend

class TaxViewSet(viewsets.ModelViewSet):
    serializer_class = TaxSerializer
    queryset = Tax.objects.all()
    http_method_names = ['post']

class TestTaxViewSet(viewsets.ModelViewSet):
    serializer_class = TestTaxSerializer
    queryset = Tax.objects.all()
    http_method_names = ['post']

class NotesViewSet(viewsets.ModelViewSet):
    serializer_class = NotesSerializer
    queryset = Tax.objects.all()
    http_method_names = ['get']
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['company', 'created']

    def get_queryset(self):
        user = self.request.user
        try:
            return  Tax.objects.filter(company__restaurant=user.employer.restaurant).order_by('created')
        except AttributeError:
            return Tax.objects.none()
