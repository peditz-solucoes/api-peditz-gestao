from django.shortcuts import render

from rest_framework import (
    viewsets,
)

from ..models import (
    User,
)

from .serializers import (
    UserSerializer,
)

class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    

    def get_queryset(self):
        queryset = User.objects.filter(id=self.request.user.id)
        if self.request.user.is_superuser:
            queryset = User.objects.all()
        return queryset
