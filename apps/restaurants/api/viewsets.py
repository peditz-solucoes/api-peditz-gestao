

from rest_framework import viewsets
from apps.restaurants.models import Restaurant
from .serializers import RestaurantSerializer
from drf_spectacular.utils import extend_schema
from rest_framework.permissions import IsAuthenticated

@extend_schema(tags=['Restaurants'])
class RestaurantViewSet(viewsets.ModelViewSet):
    queryset = Restaurant.objects.all()
    serializer_class = RestaurantSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return Restaurant.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)