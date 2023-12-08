from rest_framework import serializers

from apps.restaurants.api.serializers import RestaurantSerializer

from ..models import Client, ClientAdress, DeliveryOrder, DeliveryStatus, DeliveryRestaurantConfig

from apps.financial.models import PaymentMethod, PaymentGroup, Cashier, Payment
from apps.financial.api.serializers import OrderGroupListSerializer, ListPaymentsGroupsSerializer

from django.db import transaction

from datetime import datetime , timezone

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
    made_product = serializers.BooleanField(write_only=True, required=False, default=False)
    class Meta:
        model = DeliveryStatus
        fields = '__all__'
        read_only_fields = [
            'time'
        ]  

    def create(self, validated_data):
        status = validated_data.get('title', None)
        order = validated_data.get('order', None)
        if status == 'CANCELED' and not validated_data.get('made_product', False):
            orders = order.order_group.orders.all()
            for order in orders:
                order.active = False
                order.save()

        last_status = DeliveryStatus.objects.filter(order=order).order_by('position').last()
        if last_status:
            time_spent = datetime.now(timezone.utc) - last_status.created
            last_status.time = time_spent.seconds
            
        return super().create({
            'title': status,
            'order': validated_data.get('order', None),
        })

class OrderSerializer(serializers.ModelSerializer):

    status = serializers.SerializerMethodField(read_only=True)
    payment_method = PaymentMethodsSerializer(read_only=True)
    order_group = OrderGroupListSerializer(read_only=True)
    payment_group = ListPaymentsGroupsSerializer(read_only=True)
    class Meta:
        model = DeliveryOrder
        fields = '__all__'

    def get_status(self, obj):
        status = DeliveryStatus.objects.filter(order=obj).order_by('position')
        return DeliveryStatusSerializer(status, many=True).data

class DeliveryConfigSerializer(serializers.ModelSerializer):
    restaurant = RestaurantSerializer(read_only=True)
    class Meta:
        model = DeliveryRestaurantConfig
        fields = '__all__'

class PaymentDelveryserializer(serializers.ModelSerializer):
    payments_types = serializers.JSONField(write_only=True)
    order = serializers.PrimaryKeyRelatedField(queryset=DeliveryOrder.objects.all(), write_only=True)
    class Meta:
        model = PaymentGroup
        fields = '__all__'
        read_only_fields = [
            'cashier',
            'type',
            'total',
            'tip'
        ]

    @transaction.atomic
    def create(self, validated_data):
        payments = validated_data.get('payments_types', None)
        if not payments:
            raise serializers.ValidationError('Pagamento não informado')
        
        user = self.context.get('request').user
        restaurant = None
        try:
            restaurant = user.employer.restaurant
        except AttributeError:
            restaurant = user.restaurants
        try:
            cashier = Cashier.objects.get(restaurant=restaurant, open=True)
        except Cashier.DoesNotExist:
            raise serializers.ValidationError('Caixa não aberto')
        
        payment_group = PaymentGroup.objects.create(
            tip= 0,
            total= 0,
            type= 'DELIVERY',
            cashier= cashier,
        )

        for payment_method in payments:
            try:
                method = PaymentMethod.objects.get(id=payment_method['id'])
            except PaymentMethod.DoesNotExist:
                raise serializers.ValidationError({"detail":"Forma de pagamento não encontrada."})
            payment = Payment.objects.create(
                payment_group=payment_group,
                payment_method=method,
                value=payment_method['value'],
                type=payment_method.get('type', 'PAYMENT')
            )
            payment.save()

        order = validated_data.get('order', None)

        if order.payment_group is not None:
            raise serializers.ValidationError({"detail":"Pedido já possui pagamento"})

        order.payment_group = payment_group
        order.save()

        return payment_group

        


        