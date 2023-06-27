from django.shortcuts import render
from drf_spectacular.utils import extend_schema

from rest_framework import (
    viewsets,
)

from ..models import (
    User,
)

from .serializers import (
    UserSerializer,
)

@extend_schema(tags=['auth'])
class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    

    def get_queryset(self):
        queryset = User.objects.filter(id=self.request.user.id)
        if self.request.user.is_superuser:
            queryset = User.objects.all()
        return queryset
