
from datetime import datetime
from rest_framework import serializers

from apps.financial.models import Cashier, Bill
from apps.restaurants.models import Restaurant, Employer
from apps.user.api.serializers import UserSerializer
from apps.restaurants.api.serializers import RestaurantSerializer
from django.contrib.auth.hashers import check_password

class UserCashierSerializer(UserSerializer):
    class Meta:
        model = UserSerializer.Meta.model
        fields = ['id', 'username', 'first_name', 'last_name', 'email']
class RestaurantCashierSerializer(UserSerializer):
    class Meta:
        model = RestaurantSerializer.Meta.model
        fields = ['id', 'title']

class CashierSerializer(serializers.ModelSerializer):
    opened_by = UserCashierSerializer(read_only=True)
    closed_by = UserCashierSerializer(read_only=True)
    restaurant = RestaurantCashierSerializer(read_only=True)
    password = serializers.CharField(write_only=True, required=True)
    class Meta:
        model = Cashier
        fields = ['id', 'open','identifier', 'initial_value', 'closed_at', 'opened_by', 'opened_by_name', 'closed_by', 'closed_by_name', 'restaurant', 'created', 'password']
        read_only_fields = ['restaurant', 'opened_by', 'opened_by_name', 'closed_by', 'closed_by_name', 'closed_at', 'created']

    def validate(self, data):
        
        return data

    def create(self, validated_data):
        user = self.context['request'].user

        if not check_password(validated_data['password'], user.password):
            raise serializers.ValidationError({"detail":"Senha incorreta."})
        try:
            restaurant= Restaurant.objects.get(owner=user)
        except Restaurant.DoesNotExist:
            restaurant = None
            try:
                employer = Employer.objects.get(user=user)
                restaurant = employer.restaurant
            except Employer.DoesNotExist:
                raise serializers.ValidationError({"detail":"Este usuário não é funcionário de nenhum restaurante."})
        validated_data['restaurant'] = restaurant
        if Cashier.objects.filter(restaurant=restaurant, open=True).exists() and validated_data['open'] == True:
            raise serializers.ValidationError({"detail":"Já existe um caixa aberto para este restaurante."})
        if not validated_data['open']:
            validated_data['closed_by'] = user
            validated_data['closed_at'] = datetime.now()
        validated_data['opened_by'] = user
        return super().create(
            {
                'open':validated_data.get('open', True),
                'identifier':validated_data.get('identifier', None),
                'initial_value':validated_data.get('initial_value', 0),
                'restaurant':validated_data.get('restaurant', None),
                'opened_by':validated_data['opened_by'],
                'closed_by':validated_data.get('closed_by', None),
                'closed_at':validated_data.get('closed_at', None)

            }
        )
    
    def update(self, instance, validated_data):
        user = self.context['request'].user
        if not check_password(validated_data['password'], user.password):
            raise serializers.ValidationError({"detail":"Senha incorreta."})
        try:
            restaurant= Restaurant.objects.get(owner=user)
        except Restaurant.DoesNotExist:
            restaurant = None
            try:
                employer = Employer.objects.get(user=user)
                restaurant = employer.restaurant
            except Employer.DoesNotExist:
                raise serializers.ValidationError({"detail":"Este usuário não é funcionário de nenhum restaurante."})
        validated_data['restaurant'] = restaurant
        if Cashier.objects.filter(restaurant=restaurant, open=True).exists() and validated_data['open'] == True:
            if Cashier.objects.get(restaurant=restaurant, open=True).id != instance.id:
                raise serializers.ValidationError({"detail":"Já existe um caixa aberto para este restaurante."})
        if not validated_data['open']:
            validated_data['closed_by'] = user
            validated_data['closed_at'] = datetime.now()
        else:
            validated_data['closed_by'] = None
            validated_data['closed_at'] = None
        return super().update(instance, {
            'open':validated_data.get('open', instance.open),
            'identifier':validated_data.get('identifier', instance.identifier),
            'initial_value':validated_data.get('initial_value', instance.initial_value),
            'restaurant':validated_data.get('restaurant', instance.restaurant),
            'closed_by':validated_data.get('closed_by', None),
            'closed_at':validated_data.get('closed_at', None)
        })
    

class BillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bill
        fields = '__all__'
        read_only_fields = ['tip']