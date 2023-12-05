from rest_framework import serializers

from apps.restaurants.api.serializers import RestaurantSerializer

from ..models import Client, ClientAdress, DeliveryOrder, DeliveryStatus, DeliveryRestaurantConfig

from apps.financial.models import PaymentMethod
from apps.financial.api.serializers import OrderGroupListSerializer


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
            'restaurant',
            'needs_change',
        ]


class DeliveryStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryStatus
        fields = '__all__'

class OrderSerializer(serializers.ModelSerializer):

    status = DeliveryStatusSerializer(read_only=True, many=True)
    payment_method = PaymentMethodsSerializer(read_only=True)
    order_group = OrderGroupListSerializer(read_only=True)
    class Meta:
        model = DeliveryOrder
        fields = '__all__'

class DeliveryConfigSerializer(serializers.ModelSerializer):
    restaurant = RestaurantSerializer(read_only=True)
    class Meta:
        model = DeliveryRestaurantConfig
        fields = '__all__'