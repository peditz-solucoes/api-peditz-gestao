from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from apps.ifood.api.serializers import AuthCodeSerializer, AuthTokenSerializer, MerchantsSerializer
from peditz.ifood import IfoodClientApi
from rest_framework.permissions import IsAuthenticated
from ..models import IfoodUserCredentials
ifood_api = IfoodClientApi()


class IfoodAuthCodeViewSet(viewsets.ModelViewSet):
    serializer_class = AuthCodeSerializer
    queryset = []
    http_method_names = ['post']
    permmision_classes = (IsAuthenticated, )

class IfoodAuthTokenViewSet(viewsets.ModelViewSet):
    serializer_class = AuthTokenSerializer
    queryset = []
    http_method_names = ['post']
    permmision_classes = (IsAuthenticated,)

class IfoodMerchantsViewSet(viewsets.ModelViewSet):
    serializer_class = MerchantsSerializer
    http_method_names = ['get']
    permmision_classes = (IsAuthenticated,)

    def get_queryset(self):
        try:
            user = self.request.user
            restaurant = user.employer.restaurant
        except AttributeError:
            try:
                restaurant = user.restaurants
            except AttributeError:
                raise Response({"detail":"Este usuário não possui um restaurante."}, status=status.HTTP_400_BAD_REQUEST)
        
        try: 
            user_credentials = IfoodUserCredentials.objects.get(restaurant=restaurant)
        except IfoodUserCredentials.DoesNotExist:
            raise Response({"detail":"Este restaurante não possui credenciais para acessar a API do Ifood."}, status=status.HTTP_400_BAD_REQUEST)

        
        response  = ifood_api.get_merchants(token=user_credentials.token)

        return response
    
    def retrieve(self, request, *args, **kwargs):
        try:
            user = self.request.user
            restaurant = user.employer.restaurant
        except AttributeError:
            try:
                restaurant = user.restaurants
            except AttributeError:
                raise Response({"detail":"Este usuário não possui um restaurante."}, status=status.HTTP_400_BAD_REQUEST)
        try: 
            user_credentials = IfoodUserCredentials.objects.get(restaurant=restaurant)
        except IfoodUserCredentials.DoesNotExist:
            raise Response({"detail":"Este restaurante não possui credenciais para acessar a API do Ifood."}, status=status.HTTP_400_BAD_REQUEST)
        
        response = ifood_api.get_merchant(
            token=user_credentials.token,
            merchant_id=kwargs['pk']
        )

        return Response(response, status=status.HTTP_200_OK)
        
        
