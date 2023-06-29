

from rest_framework import viewsets
from apps.restaurants.models import Restaurant
from .serializers import RestaurantSerializer
from rest_framework.permissions import IsAuthenticated

class RestaurantViewSet(viewsets.ModelViewSet):
    queryset = Restaurant.objects.all()
    serializer_class = RestaurantSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Restaurant.objects.all()    
        return Restaurant.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)