from rest_framework import serializers
from ..models import Client, ClientAdress

from apps.financial.models import PaymentMethod


class ClientAdressSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClientAdress
        fields = '__all__'

class ClientSerializer(serializers.ModelSerializer):
    adresses = serializers.SerializerMethodField()
    class Meta:
        model = Client
        fields = '__all__'

    def get_adresses(self, obj):
        adresses = ClientAdress.objects.filter(client=obj)
        return ClientAdressSerializer(adresses, many=True).data
    
    def create(self, validated_data):

        phone = validated_data.get('phone', None)
        if phone:
            try:
                client = Client.objects.get(phone=phone)
                return client
            except Client.DoesNotExist:
                return super().create(validated_data)
            

class PaymentMethodsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentMethod
        fields = [
            'method',
            'title',
            'active',
            'id',
            'restaurant'
        ]