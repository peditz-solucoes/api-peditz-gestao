
from datetime import datetime
from rest_framework import serializers
from apps.financial.models import Cashier, Bill, Order, OrderGroup, OrderStatus, OrderComplement, OrderComplementItem
from apps.restaurants.models import Restaurant, Employer, Product, ProductComplementCategory, ProductComplementItem
from apps.user.api.serializers import UserSerializer
from apps.restaurants.api.serializers import EmployerSerializer, RestaurantSerializer, TableSerializer
from django.contrib.auth.hashers import check_password
from django.db import IntegrityError
from django.db import transaction

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
    

class TableBillSerializer(TableSerializer):
    class Meta:
        model = TableSerializer.Meta.model
        fields = ['id', 'title']

class BillSerializer(serializers.ModelSerializer):
    opened_by = UserCashierSerializer(read_only=True)
    table_datail = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = Bill
        fields = ['id', 'tip', 'opened_by', 'opened_by_name', 'table', 'cashier', 'created', 'open', 'client_name', 'client_phone', 'number', 'table_datail']
        read_only_fields = ['tip', 'opened_by', 'opened_by_name', 'cashier']

    def get_table_datail(self, obj):
        table = obj.table
        serializer = TableBillSerializer(table)
        return serializer.data

    def create (self, validated_data):
        user = self.context['request'].user
        try:
            restaurant= Restaurant.objects.get(owner=user)
        except Restaurant.DoesNotExist:
            restaurant = None
            try:
                employer = Employer.objects.get(user=user)
                restaurant = employer.restaurant
            except Employer.DoesNotExist:
                raise serializers.ValidationError({"detail":"Este usuário não é funcionário de nenhum restaurante."})
        try:
            cashier = Cashier.objects.get(open=True, restaurant=restaurant)
        except Cashier.DoesNotExist:
            raise serializers.ValidationError({"detail":"Não há caixa aberto para este restaurante."})
        validated_data['cashier'] = cashier
        if Bill.objects.filter(cashier=validated_data['cashier'], open=True, number=validated_data['number']).exists():
            raise serializers.ValidationError({"detail":"Já existe uma conta aberta com este número neste caixa."})
        validated_data['opened_by'] = user
        return super().create(
            validated_data
        )

class BillItemSerializer(serializers.ModelSerializer):
    table = TableBillSerializer(read_only=True)
    class Meta:
        model = Bill
        fields = [
            'id',
            'client_name',
            'table',
            'number',
        ]

class StatusOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderStatus
        fields = ['id', 'status']


class EmployerOrderSerializer(EmployerSerializer):
    class Meta:
        model = EmployerSerializer.Meta.model
        fields = ['id', 'first_name', 'last_name']
class OrderGroupSerialier(serializers.ModelSerializer):
    bill = BillItemSerializer(read_only=True)
    status = StatusOrderSerializer(read_only=True)
    restaurant = RestaurantCashierSerializer(read_only=True)
    collaborator = EmployerOrderSerializer(read_only=True)
    bill_id = serializers.PrimaryKeyRelatedField(write_only=True, queryset=Bill.objects.all(), source='bill')
    operator_code = serializers.CharField(write_only=True, allow_blank=True, allow_null=True)
    order_items = serializers.JSONField(write_only=True)
    class Meta:
        model = OrderGroup
        fields = [
            'id',
            'bill',
            'status',
            'created',
            'collaborator_name',
            'collaborator',
            'total',
            'order_number',
            'restaurant',
            'type',
            'bill_id',
            'operator_code',
            'order_items'
        ]
        read_only_fields = ['collaborator_name', 'total', 'order_number', 'type']
    @transaction.atomic
    def create(self, validated_data):
        user = self.context['request'].user
        restaurant = None
        employer = None
        if validated_data.get('bill', None) is None:
            raise serializers.ValidationError({"detail":"É necessário informar uma conta."})
        if validated_data.get('operator_code', None) == '' or validated_data.get('operator_code', None) == None:
            if user.employer:
                employer = user.employer
                restaurant = employer.restaurant
            else:
                raise serializers.ValidationError({"detail":"Este usuário não é funcionário de nenhum restaurante."})
        else:
            try:
                employer = Employer.objects.get(code=validated_data.get('operator_code', None))
                restaurant = employer.restaurant
            except Employer.DoesNotExist:
                raise serializers.ValidationError({"detail":"Código de operador inválido."})
        if restaurant is None:
            raise serializers.ValidationError({"detail":"Este usuário não é funcionário de nenhum restaurante."})
        validated_data['restaurant'] = restaurant
        validated_data['collaborator'] = employer
        validated_data['status'] = OrderStatus.objects.all().order_by('order').first()
        orders = validated_data.get('order_items', None)
        order_group = super().create({
            'bill':validated_data.get('bill', None),
            'status':validated_data.get('status', None),
            'collaborator':validated_data.get('collaborator', None),
            'restaurant':validated_data.get('restaurant', None),
            'type':'BILL',
            'total':0,
        })
        if orders is None:
            raise serializers.ValidationError({"detail":"É necessário informar os itens do pedido."})
        for order in orders:
            order_db = None
            try: 
                product = Product.objects.get(id=order['product_id'])
                order_db = Order.objects.create(
                    product=product,
                    quantity=order['quantity'],
                    order_group=order_group,
                    product_title=product.title,
                )
                order_db.save()
                if len(order['complements'])> 0:
                    for complement in order['complements']:
                        if len(complement['items']) > 0:
                            try:
                                complement_group = ProductComplementCategory.objects.get(id=complement['complement_id'])
                            except ProductComplementCategory.DoesNotExist:
                                raise serializers.ValidationError({"detail":"Categoria de complemento não encontrada."})
                            complement_db = OrderComplement.objects.create(
                                order=order_db,
                                complement_group=complement_group,
                            )
                            complement_db.save()
                            if len(complement['items']):
                                for item in complement['items']:
                                    try:
                                        complement_item = ProductComplementItem.objects.get(id=item['item_id'])
                                    except ProductComplementItem.DoesNotExist:
                                        raise serializers.ValidationError({"detail":"Complemento não encontrado."})
                                    complement_item_db = OrderComplementItem.objects.create(
                                        order_complement=complement_db,
                                        complement=complement_item,
                                        quantity=item['quantity'],
                                    )
                                    complement_item_db.save()
                        

            except Product.DoesNotExist:
                raise serializers.ValidationError({"detail":"Produto não encontrado."})
        return order_group