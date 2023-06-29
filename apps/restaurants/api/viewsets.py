

from rest_framework import viewsets
from apps.restaurants.models import Restaurant, Employer
from .serializers import RestaurantSerializer, EmployerSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status


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

class EmployerViewSet(viewsets.ModelViewSet):
    queryset = Employer.objects.all()
    serializer_class = EmployerSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Employer.objects.all()  
        if Restaurant.objects.filter(owner=self.request.user).exists():
            return Employer.objects.filter(restaurant__owner=self.request.user)
        return Employer.objects.filter(user=self.request.user)
    
    def create(self, request, *args, **kwargs):
        if not Restaurant.objects.filter(owner=request.user).exists():
            return Response({"detail": "You must be an owner of a restaurant to create an employer."}, status=status.HTTP_403_FORBIDDEN)

        return super().create(request, *args, **kwargs)
