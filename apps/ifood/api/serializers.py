
from rest_framework import serializers

from peditz.ifood import IfoodClientApi
from ..models import IfoodUserCredentials
ifood_api = IfoodClientApi()

class AuthTokenSerializer (serializers.Serializer):
    authorizationCode = serializers.CharField(max_length=255, write_only=True)
    authorizationCodeVerifier = serializers.CharField(max_length=255, write_only=True)
    accessToken = serializers.CharField(max_length=255, read_only=True)
    refreshToken = serializers.CharField(max_length=255, read_only=True)
    expiresIn = serializers.IntegerField(read_only=True)
    type = serializers.CharField(max_length=255, read_only=True)

    class Meta:
        fields = ['client_id', 'userCode', 'verificationUrl', 'expiresIn', 'verificationUrlComplete', 'authorizationCodeVerifier']

    def create(self, validated_data):
        user = self.context['request'].user
        restaurant = None
        try:  
            restaurant = user.employer.restaurant
        except AttributeError:
            try:
                restaurant = user.restaurants
            except AttributeError:
                raise serializers.ValidationError({"detail":"Este usuário não possui um restaurante."})
        response  = ifood_api.get_auth_token(
            authorization_code=validated_data['authorizationCode'],
            authorization_code_verifier=validated_data['authorizationCodeVerifier']
        )
        
        try:
            user_credentials = IfoodUserCredentials.objects.get(restaurant=restaurant)
            user_credentials.token = response['accessToken']
            user_credentials.token_type = response['type']
            user_credentials.expires_in = response['expiresIn']
            user_credentials.refresh_token = response['refreshToken']
            user_credentials.save()
        except IfoodUserCredentials.DoesNotExist:
            IfoodUserCredentials.objects.create(
                token=response['accessToken'],
                token_type=response['type'],
                expires_in=response['expiresIn'],
                refresh_token=response['refreshToken'],
                restaurant=restaurant
            )

        return response
    
class AuthCodeSerializer (serializers.Serializer):
    userCode = serializers.CharField(max_length=255, read_only=True)
    verificationUrl = serializers.CharField(max_length=255, read_only=True)
    expiresIn = serializers.IntegerField(read_only=True)
    verificationUrlComplete = serializers.CharField(max_length=255, read_only=True)
    authorizationCodeVerifier = serializers.CharField(max_length=255, read_only=True)
    class Meta:
        fields = ['client_id', 'userCode', 'verificationUrl', 'expiresIn', 'verificationUrlComplete', 'authorizationCodeVerifier']

    def create(self, validated_data):
        response  = ifood_api.get_user_code()
        return response
    

class MerchantsSerializer (serializers.Serializer):
    id = serializers.CharField(max_length=255, read_only=True)
    name = serializers.CharField(max_length=255, read_only=True)
    corporateName = serializers.CharField(max_length=255, read_only=True)

    class Meta:
        fields = ['id', 'name', 'corporateName']