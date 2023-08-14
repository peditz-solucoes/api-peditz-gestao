from rest_framework import viewsets

from .serializers import  TaxSerializer
from ..models import Tax

class TaxViewSet(viewsets.ModelViewSet):
    serializer_class = TaxSerializer
    queryset = Tax.objects.all()
