
from datetime import datetime
import json
from uuid import UUID
from rest_framework import serializers
from apps.financial.models import Cashier, Bill, Order, OrderGroup, OrderStatus, OrderComplement, OrderComplementItem, PaymentMethod, PaymentGroup, Payment, TakeoutOrder, CancelationReason
from apps.restaurants.models import Restaurant, Employer, Product, ProductComplementCategory, ProductComplementItem, ProductPrice, ComplementPrice
from apps.user.api.serializers import UserSerializer
from apps.restaurants.api.serializers import EmployerSerializer, RestaurantSerializer, TableSerializer
from django.contrib.auth.hashers import check_password
from django.db import transaction
from apps.delivery.models import Client, DeliveryRestaurantConfig, DeliveryOrder, ClientAdress, DeliveryStatus

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
class UUIDEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, UUID):
            # if the obj is uuid, we simply return the value of uuid
            return obj.hex
        return json.JSONEncoder.default(self, obj)
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
        if restaurant.active is False:
            raise serializers.ValidationError({"detail":"No momento seu acesso está suspenso, para regularizar seu pagamento procure o suporte pelo Whatsapp +55 11 93947‑4125"})
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
    bill_id = serializers.PrimaryKeyRelatedField(write_only=True, queryset=Bill.objects.filter(), source='bill')
    operator_code = serializers.CharField(write_only=True, allow_blank=True, allow_null=True, required=False)
    from_app = serializers.BooleanField(write_only=True, default=False)
    order_items = serializers.JSONField()
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
            'order_items',
            'from_app',
            'cashier',
        ]
        read_only_fields = ['collaborator_name', 'total', 'order_number', 'type']
    @transaction.atomic
    def create(self, validated_data):
        user = self.context['request'].user
        restaurant = None
        employer = None
        if validated_data.get('bill', None) is None:
            raise serializers.ValidationError({"detail":"É necessário informar uma conta."})
        if validated_data.get('bill', None).open == False:
            raise serializers.ValidationError({"detail":"Conta já foi fechada."})
        if validated_data.get('operator_code', None) == '' or validated_data.get('operator_code', None) == None:
            if user.employer:
                employer = user.employer
                restaurant = employer.restaurant
            else:
                raise serializers.ValidationError({"detail":"Este usuário não é funcionário de nenhum restaurante."})
        else:
            try:
                employer = Employer.objects.get(code=validated_data.get('operator_code', None), restaurant=validated_data.get('bill', None).cashier.restaurant)
                restaurant = employer.restaurant
            except Employer.DoesNotExist:
                raise serializers.ValidationError({"detail":"Código de operador inválido."})
        if restaurant is None:
            raise serializers.ValidationError({"detail":"Este usuário não é funcionário de nenhum restaurante."})
        validated_data['restaurant'] = restaurant
        validated_data['collaborator'] = employer
        validated_data['status'] = OrderStatus.objects.filter(
            restaurant=restaurant,
        ).order_by('order').first()
        orders = validated_data.get('order_items', None)
        order_group = super().create({
            'bill':validated_data.get('bill', None),
            'status':validated_data.get('status', None),
            'collaborator':validated_data.get('collaborator', None),
            'restaurant':validated_data.get('restaurant', None),
            'type':'BILL',
            'cashier': restaurant.cashiers.filter(open=True).first(),
            'total':0,
        })
        order_items_output = []
        if orders is None or len(orders) == 0:
            raise serializers.ValidationError({"detail":"É necessário informar os itens do pedido."})
        for order in orders:
            order_db = None
            try: 
                product = Product.objects.get(id=order['product_id'])
                if product.printer is not None:
                    printer = product.printer.name
                else:
                    printer = None
                order_items_output.append({
                    'product_id':  order['product_id'],
                    'product_title':  product.title,
                    'notes': order.get('notes', ''),
                    'quantity': order['quantity'],
                    'printer_name': printer,
                    'items': [],
                })
                order_db = Order.objects.create(
                    product=product,
                    note=order.get('notes', ''),
                    quantity=order['quantity'],
                    unit_price=product.price,
                    order_group=order_group,
                    product_title=product.title,
                    total=float(product.price)* float(order['quantity']),
                )
                order_db.save()
                if len(order['complements'])> 0:
                    for complement in order['complements']:
                        order_items_output[-1]['items'].append({
                            'complement_id': complement['complement_id'],
                            'complement_title': complement['complement_title'],
                            'items': [],
                        })
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
                                    order_items_output[-1]['items'][-1]['items'].append({
                                        'item_id': item['item_id'],
                                        'item_title': item['item_title'],
                                        'quantity': item['quantity'],
                                    })
                                    try:
                                        complement_item = ProductComplementItem.objects.get(id=item['item_id'])
                                    except ProductComplementItem.DoesNotExist:
                                        raise serializers.ValidationError({"detail":"Complemento não encontrado."})
                                    complement_item_db = OrderComplementItem.objects.create(
                                        order_complement=complement_db,
                                        complement=complement_item,
                                        unit_price=complement_item.price,
                                        quantity=item['quantity'],
                                    )
                                    complement_item_db.save()
                        

            except Product.DoesNotExist:
                raise serializers.ValidationError({"detail":"Produto não encontrado."})
        order_group.order_items = order_items_output
        json_r = {
            "id": order_group.id,
            "bill": BillSerializer(order_group.bill).data,
            "status": {
                "id": order_group.status.id,
                "status": order_group.status.status
            },
            "created": str(order_group.created),
            "collaborator_name": order_group.collaborator_name,
            "collaborator": EmployerOrderSerializer(order_group.collaborator).data,
            "total": str(order_group.total),
            "order_number": order_group.order_number,
            "restaurant": {
                "id": validated_data.get('restaurant', None).id or None,
                "title": validated_data.get('restaurant', None).title or None,
            },
            "type": order_group.type,
            "order_items": order_group.order_items
        }

        if validated_data.get('from_app', False):
            channel_layer = get_channel_layer()
            json_ws = json_r.copy()
            json_ws['bill']['table'] = json_ws['bill']['table_datail']
            async_to_sync(channel_layer.group_send)(
                "pedidos_%s" % restaurant.id,
                {"type": "order",
                    "message": json.dumps(json_ws, cls=UUIDEncoder)
                }
            )
        return order_group

class ComplementItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderComplementItem
        fields = [
            'id',
            'complement_title',
            'quantity',
            'unit_price',
            'total',
        ]
class ComplementSerializer(serializers.ModelSerializer):
    items = ComplementItemSerializer(many=True, read_only=True)
    class Meta:
        model = OrderComplement
        fields = ['complement_group_title', 'items', 'id', 'total', ]

class ProductListOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = [
            'id',
            'title',
            'price',
        ]
class OrderSerializer(serializers.ModelSerializer):
    complements = ComplementSerializer(many=True, read_only=True)
    product = ProductListOrderSerializer(read_only=True)
    class Meta:
        model = Order
        fields = [
            'id',
            'product_title',
            'quantity',
            'unit_price',
            'note',
            'total',
            'product',
            'complements'
        ]

class OrderGroupListSerializer(serializers.ModelSerializer):
    orders = OrderSerializer(many=True, read_only=True)
    status = StatusOrderSerializer(read_only=True)
    bill = BillItemSerializer(read_only=True)
    class Meta:
        model = OrderGroup
        fields = [
            'id',
            'created',
            'collaborator_name',
            'total',
            'order_number',
            'type',
            'orders',
            'status',
            'modified',
            'bill',
        ]

class DeleteOrderSerializer(serializers.ModelSerializer):
    operator_code = serializers.CharField(write_only=True)
    order_id = serializers.PrimaryKeyRelatedField(queryset=Order.objects.all(), write_only=True)
    message = serializers.CharField(read_only=True)
    reason = serializers.CharField(write_only=True, allow_blank=True, allow_null=True, required=False)
    class Meta:
        model = Order
        fields = ['id', 'operator_code', 'order_id', 'message', 'reason']

    def create(self, validated_data):
        try:
            employer = Employer.objects.get(code=validated_data.get('operator_code', None), restaurant=validated_data.get('order_id', None).order_group.restaurant)
        except Employer.DoesNotExist:
            raise serializers.ValidationError({"detail":"Código de operador inválido."})
        try:
            order = Order.objects.get(id=validated_data.get('order_id', None).id)
        except Order.DoesNotExist:
            raise serializers.ValidationError({"detail":"Pedido não encontrado."})
        
        try:
            cashier = Cashier.objects.get(open=True, restaurant=order.order_group.restaurant)
        except Cashier.DoesNotExist:
            raise serializers.ValidationError({"detail":"Não há caixa aberto para este restaurante."})
        
        cancelation_reason = CancelationReason.objects.create(
            title="Cancelamento de pedido",
            type="ORDER",
            restaurant=order.order_group.restaurant,
            reason=validated_data.get('reason', ''),
            operator=employer.user,
            product=order.product,
            product_title=order.product_title,
            cashier=cashier,
            quantity=order.quantity,
        )
        cancelation_reason.save()
        order.delete()

        validated_data['message'] = 'Pedido excluído com sucesso.'
        return validated_data
    
class PaymentsMethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentMethod
        fields = '__all__'


class PaymentGroupSerializer(serializers.ModelSerializer):
    pyments_methods = serializers.JSONField(write_only=True)
    bills = serializers.JSONField(write_only=True)
    class Meta:
        model = PaymentGroup
        fields = '__all__'
        read_only_fields = ['tip', 'total', 'cashier', 'type']

    @transaction.atomic
    def create(self, validated_data):
        user = self.context['request'].user
        discount = validated_data.get('discount', 0)
        cashier = None
        try: 
            cashier = Cashier.objects.get(restaurant=user.employer.restaurant, open=True)
        except Cashier.DoesNotExist:
            raise serializers.ValidationError({"detail":"Caixa não encontrado."})
        payment_group = PaymentGroup.objects.create(
            tip= 0,
            total= 0,
            type= 'BILL',
            cashier= cashier,
            discount=discount,
        )
        bills = validated_data.get('bills', None)
        if bills is None or len(bills) == 0:
            raise serializers.ValidationError({"detail":"É necessário informar os itens do pedido."})
        for bill in bills:
            try:
                bill_db = Bill.objects.get(id=bill)
                if bill_db.open == False:
                    raise serializers.ValidationError({"detail":"Conta já foi fechada."})
                bill_db.payment_group = payment_group
                bill_db.open = False
                bill_db.save()
            except Bill.DoesNotExist:
                raise serializers.ValidationError({"detail":"Conta não encontrada."})
            
        if len(validated_data.get('pyments_methods', [])) > 0:
            for payment_method in validated_data.get('pyments_methods', []):
                try:
                    method = PaymentMethod.objects.get(id=payment_method['id'])
                except PaymentMethod.DoesNotExist:
                    raise serializers.ValidationError({"detail":"Forma de pagamento não encontrada."})
                payment = Payment.objects.create(
                    payment_group=payment_group,
                    payment_method=method,
                    value=payment_method['value'],
                )
                payment.save()
        else:
            raise serializers.ValidationError({"detail":"É necessário informar as formas de pagamento."})
        return payment_group
    

class PaymentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__' 

class BillOnPaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bill
        fields = [
            'id',
            'number'
        ]

class PaymentMethodListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields= [
            'payment_method_title',
            'value',
            'note',
            'created',
            'id',
            'type',
]

class ListPaymentsGroupsSerializer(serializers.ModelSerializer):
    payments = PaymentMethodListSerializer(many=True, read_only=True)
    bills = BillOnPaymentSerializer(many=True, read_only=True)
    class Meta:
        model = PaymentGroup
        fields = '__all__'


class CloseBillSerializer(serializers.ModelSerializer):
    operator_code = serializers.CharField(write_only=True)
    bill_id = serializers.PrimaryKeyRelatedField(queryset=Bill.objects.filter(open=True), write_only=True)
    message = serializers.CharField(read_only=True)
    reason = serializers.CharField(write_only=True, allow_blank=True, allow_null=True, required=False)
    class Meta:
        model = Bill
        fields = ['id', 'operator_code', 'bill_id', 'message', 'reason']
        read_only_fields = ['message', 'id']
    
    @transaction.atomic
    def create(self, validated_data):
        try:
            employer = Employer.objects.get(code=validated_data.get('operator_code', None), restaurant=validated_data.get('bill_id', None).cashier.restaurant) 
            if employer.role != 'GERENTE':
                raise serializers.ValidationError({"detail":"Este usuário não é gerente."})
        except Employer.DoesNotExist:
            raise serializers.ValidationError({"detail":"Código de operador inválido."})
        try:
            bill = Bill.objects.get(id=validated_data.get('bill_id', None).id)
        except Bill.DoesNotExist:
            raise serializers.ValidationError({"detail":"Conta não encontrada."})
        bill.open = False
        bill.save()

        cr = CancelationReason.objects.create(
            title="Fechamento de conta",
            type="BILL",
            restaurant=bill.cashier.restaurant,
            reason=validated_data.get('reason', ''),
            operator=employer.user,
            cashier=bill.cashier,
            bill=bill,
        )
        cr.save()
        validated_data['message'] = 'Conta fechada com sucesso.'
        return validated_data
    
class TakeOutOurderSerialier(serializers.ModelSerializer):
    status = StatusOrderSerializer(read_only=True)
    restaurant = RestaurantCashierSerializer(read_only=True)
    collaborator = EmployerOrderSerializer(read_only=True)
    from_app = serializers.BooleanField(write_only=True, default=False)
    order_items = serializers.JSONField()
    payment_methods = serializers.JSONField(write_only=True)
    client_name = serializers.CharField(write_only=True, allow_blank=True, allow_null=True, required=False)
    client_phone = serializers.CharField(write_only=True, allow_blank=True, allow_null=True, required=False)
    cpf = serializers.CharField(write_only=True, allow_blank=True, allow_null=True, required=False)
    takeout_order = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = OrderGroup
        fields = [
            'id',
            'status',
            'created',
            'collaborator_name',
            'collaborator',
            'total',
            'order_number',
            'restaurant',
            'type',
            'notes',
            'order_items',
            'from_app',
            'payment_methods',
            'client_name',
            'client_phone',
            'cpf',
            'takeout_order'
        ]
        read_only_fields = ['collaborator_name', 'total', 'order_number', 'type', 'restaurant']
    
    def get_takeout_order(self, obj):
        try:
            takeout = TakeoutOrder.objects.get(order_group=obj)
            return takeout.sequence
        except TakeoutOrder.DoesNotExist:
            return None
    @transaction.atomic
    def create(self, validated_data):
        user = self.context['request'].user
        restaurant = None
        employer = None
        if user.employer:
            employer = user.employer
            restaurant = employer.restaurant
        else:
            raise serializers.ValidationError({"detail":"Este usuário não é funcionário de nenhum restaurante."})
        if restaurant is None:
            raise serializers.ValidationError({"detail":"Este usuário não é funcionário de nenhum restaurante."})
        
        validated_data['restaurant'] = restaurant
        validated_data['collaborator'] = employer
        
        validated_data['status'] = OrderStatus.objects.filter(
            restaurant=restaurant,
        ).order_by('order').first()

        orders = validated_data.get('order_items', None)
        order_group = super().create({
            'status':validated_data.get('status', None),
            'collaborator':validated_data.get('collaborator', None),
            'restaurant':validated_data.get('restaurant', None),
            'type':'TAKEOUT',
            'total':0,
            'notes':validated_data.get('notes', None),
            'cashier': restaurant.cashiers.filter(open=True).first(),
        })

        order_items_output = []
        
        if orders is None or len(orders) == 0:
            raise serializers.ValidationError({"detail":"É necessário informar os itens do pedido."})
        
        for order in orders:
            order_db = None
            try: 
                product = Product.objects.get(id=order['product_id'])
                if product.printer is not None:
                    printer = product.printer.name
                else:
                    printer = None
                order_db = Order.objects.create(
                    product=product,
                    note=order.get('notes', ''),
                    quantity=order['quantity'],
                    unit_price=product.price,
                    order_group=order_group,
                    product_title=product.title,
                    total=float(product.price)* float(order['quantity']),
                )
                order_db.save()
                order_items_output.append({
                    'product_id':  order['product_id'],
                    'product_title':  product.title,
                    'product_price': product.price,
                    'notes': order.get('notes', ''),
                    'quantity': order['quantity'],
                    'printer_name': printer,
                    'items': [],
                    'id': order_db.id,

                })
                if len(order['complements'])> 0:
                    for complement in order['complements']:
                        order_items_output[-1]['items'].append({
                            'complement_id': complement['complement_id'],
                            'complement_title': complement['complement_title'],
                            'items': [],
                        })
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
                                    order_items_output[-1]['items'][-1]['items'].append({
                                        'item_id': item['item_id'],
                                        'item_title': item['item_title'],
                                        'quantity': item['quantity'],
                                    })
                                    try:
                                        complement_item = ProductComplementItem.objects.get(id=item['item_id'])
                                    except ProductComplementItem.DoesNotExist:
                                        raise serializers.ValidationError({"detail":"Complemento não encontrado."})
                                    complement_item_db = OrderComplementItem.objects.create(
                                        order_complement=complement_db,
                                        complement=complement_item,
                                        unit_price=complement_item.price,
                                        quantity=item['quantity'],
                                    )
                                    complement_item_db.save()
                        

            except Product.DoesNotExist:
                raise serializers.ValidationError({"detail":"Produto não encontrado."})
        order_group.order_items = order_items_output
        cashier = None
        try:
            cashier = Cashier.objects.get(open=True, restaurant=restaurant)
        except Cashier.DoesNotExist:
            raise serializers.ValidationError({"detail":"Não há caixa aberto para este restaurante."})

        payment_group = PaymentGroup.objects.create(
            tip= 0,
            total= 0,
            type= 'TAKEOUT',
            cashier= cashier,
        )

        if len(validated_data.get('payment_methods', [])) > 0:
            for payment_method in validated_data.get('payment_methods', []):
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
        else:
            raise serializers.ValidationError({"detail":"É necessário informar as formas de pagamento."})
        last_sequence = TakeoutOrder.objects.filter(
            order_group__restaurant=restaurant,
            created__date=datetime.now().date(),
        ).order_by('-sequence').first()
        if last_sequence is None:
            sequence = 1
        else:
            sequence = last_sequence.sequence + 1
        takeout = TakeoutOrder.objects.create(
            client_name=validated_data.get('client_name', None),
            client_phone=validated_data.get('client_phone', None),
            cpf=validated_data.get('cpf', None),
            order_group=order_group,
            cashier=cashier,
            payment_group=payment_group,
            sequence=sequence,
        )

        json_r = {
            "id": order_group.id,
            "status": {
                "id": order_group.status.id,
                "status": order_group.status.status
            },
            "created": str(order_group.created),
            "collaborator_name": order_group.collaborator_name,
            "collaborator": EmployerOrderSerializer(order_group.collaborator).data,
            "total": str(order_group.total),
            "order_number": order_group.order_number,
            "restaurant": {
                "id": validated_data.get('restaurant', None).id or None,
                "title": validated_data.get('restaurant', None).title or None,
            },
            "type": order_group.type,
            "order_items": order_group.order_items,
            "takeout_order": takeout.id,
        }


        if validated_data.get('from_app', False):
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                "pedidos_%s" % restaurant.id,
                {"type": "order",
                    "message": json.dumps(json_r, cls=UUIDEncoder)
                }
            )
        return order_group
    
class DeliveryOrderSerialier(serializers.ModelSerializer):
    status = StatusOrderSerializer(read_only=True)
    restaurant = RestaurantCashierSerializer(read_only=True)
    restaurant_id = serializers.PrimaryKeyRelatedField(queryset=Restaurant.objects.all(), write_only=True)
    from_app = serializers.BooleanField(write_only=True, default=False)
    order_items = serializers.JSONField()
    payment_method = serializers.PrimaryKeyRelatedField(queryset=PaymentMethod.objects.all(), write_only=True)
    client = serializers.PrimaryKeyRelatedField(queryset=Client.objects.all(), write_only=True)
    adress = serializers.PrimaryKeyRelatedField(queryset=ClientAdress.objects.all(), write_only=True, allow_null=True, allow_empty=True)
    troco = serializers.DecimalField(max_digits=10, decimal_places=2, write_only=True, default=0)
    takeaway = serializers.BooleanField(write_only=True, default=False)
    delivery_order = serializers.SerializerMethodField(read_only=True)
    delivery_price = serializers.DecimalField(max_digits=10, decimal_places=2, write_only=True, default=0)
    class Meta:
        model = OrderGroup
        fields = [
            'id',
            'status',
            'created',
            'total',
            'order_number',
            'restaurant',
            'type',
            'notes',
            'order_items',
            'from_app',
            'payment_method',
            'client',
            'restaurant_id',
            'adress',
            'troco',
            'takeaway',
            'delivery_order',
            'delivery_price',
        ]
        read_only_fields = ['total', 'order_number', 'type', 'restaurant']

    def get_delivery_order(self, obj):
        try:
            delivery = DeliveryOrder.objects.get(order_group=obj)
            return delivery.id
        except DeliveryOrder.DoesNotExist:
            return None
    
    @transaction.atomic
    def create(self, validated_data):
        restaurant = validated_data.get('restaurant_id', None)
        validated_data['restaurant'] = restaurant

        try:
            configs = DeliveryRestaurantConfig.objects.get(restaurant=restaurant)
        except DeliveryRestaurantConfig.DoesNotExist:
            raise serializers.ValidationError({"detail":"Este restaurante não está configurado para delivery."})
        if configs.enable_delivery == False:
            raise serializers.ValidationError({"detail":"Este restaurante não aceita delivery no momento."})
        

        validated_data['status'] = OrderStatus.objects.filter(
            restaurant=restaurant,
        ).order_by('order').first()

        orders = validated_data.get('order_items', None)

        cashier = None
        try:
            cashier = Cashier.objects.get(open=True, restaurant=restaurant)
        except Cashier.DoesNotExist:
            raise serializers.ValidationError({"detail":"Não há caixa aberto para este restaurante."})
        order_group = super().create({
            'status':validated_data.get('status', None),
            'restaurant':validated_data.get('restaurant', None),
            'type':'DELIVERY',
            'total':0,
            'notes':validated_data.get('notes', None),
            'cashier': cashier,
        })

        order_items_output = []
        
        if orders is None or len(orders) == 0:
            raise serializers.ValidationError({"detail":"É necessário informar os itens do pedido."})
        
        for order in orders:
            order_db = None
            try: 
                product_price = ProductPrice.objects.get(id=order['product_id'])
                product = product_price.product
                if product_price is None:
                    raise serializers.ValidationError({"detail":"Preço do produto inválido."})
                if product.printer is not None:
                    printer = product.printer.name
                else:
                    printer = None
                order_items_output.append({
                    'product_id':  order['product_id'],
                    'product_title':  product.title,
                    'product_price':  product_price.price,
                    'notes': order.get('notes', ''),
                    'quantity': order['quantity'],
                    'printer_name': printer,
                    'items': [],
                })
                order_db = Order.objects.create(
                    product=product,
                    note=order.get('notes', ''),
                    quantity=order['quantity'],
                    unit_price=product_price.price,
                    order_group=order_group,
                    product_title=product.title,
                    total=float(product.price)* float(order['quantity']),
                )
                order_db.save()
                if len(order['complements'])> 0:
                    for complement in order['complements']:
                        order_items_output[-1]['items'].append({
                            'complement_id': complement['complement_id'],
                            'complement_title': complement['complement_title'],
                            'items': [],
                        })
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
                                    order_items_output[-1]['items'][-1]['items'].append({
                                        'item_id': item['item_id'],
                                        'item_title': item['item_title'],
                                        'quantity': item['quantity'],
                                    })
                                    try:
                                        complement_item = ProductComplementItem.objects.get(id=item['item_id'])
                                    except ProductComplementItem.DoesNotExist:
                                        raise serializers.ValidationError({"detail":"Complemento não encontrado."})
                                    # complement_price = ComplementPrice.objects.filter(product_complement_item=complement_item, price=item['item_price']).first()
                                    # if complement_price is None:
                                    #     raise serializers.ValidationError({"detail":"Preço do complemento inválido."})
                                    complement_item_db = OrderComplementItem.objects.create(
                                        order_complement=complement_db,
                                        complement=complement_item,
                                        unit_price=complement_item.price,
                                        quantity=item['quantity'],
                                    )
                                    complement_item_db.save()
            except Product.DoesNotExist:
                raise serializers.ValidationError({"detail":"Produto não encontrado."})
        order_group.order_items = order_items_output

        delivery_price = validated_data.get('delivery_price', 0)
        delivery = DeliveryOrder.objects.create(
            client=validated_data.get('client', None),
            client_name=validated_data.get('client', None).name,
            client_phone=validated_data.get('client', None).phone,
            number = validated_data.get('adress', None).number if validated_data.get('adress', None) else None,
            street = validated_data.get('adress', None).street if validated_data.get('adress', None) else None,
            complement = validated_data.get('adress', None).complement if validated_data.get('adress', None) else None,
            neighborhood = validated_data.get('adress', None).neighborhood if validated_data.get('adress', None) else None,
            city = validated_data.get('adress', None).city if validated_data.get('adress', None) else None,
            state = validated_data.get('adress', None).state if validated_data.get('adress', None) else None,
            postal_code = validated_data.get('adress', None).postal_code if validated_data.get('adress', None) else None,
            order_group=order_group,
            delivery_price=delivery_price,
            troco=validated_data.get('troco', 0),
            payment_method=validated_data.get('payment_method', None),
            payment_method_title=validated_data.get('payment_method', None).title,
            takeaway=validated_data.get('takeaway', False),
        )

        delivery.save()

        delivery_status = DeliveryStatus.objects.create(
            order=delivery,
        )
        delivery_status.save()

        json_r = {
            "id": delivery.id,
            "status": {
                "id": order_group.status.id,
                "status": order_group.status.status
            },
            "created": str(order_group.created),
            "collaborator_name": order_group.collaborator_name,
            "collaborator": EmployerOrderSerializer(order_group.collaborator).data,
            "total": str(order_group.total),
            "order_number": order_group.order_number,
            "restaurant": {
                "id": validated_data.get('restaurant', None).id or None,
                "title": validated_data.get('restaurant', None).title or None,
            },
            "type": order_group.type,
            "order_items": order_group.order_items,
            # "takeout_order": takeout.id,
        }


        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "pedidos_%s" % restaurant.id,
            {"type": "delivery",
                "message": json.dumps({"delivery": True}, cls=UUIDEncoder)
            }
        )
        return order_group


class OrderStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderStatus
        fields = '__all__'


class CancelationReasonSerializer(serializers.ModelSerializer):
    class Meta:
        model = CancelationReason
        fields = ['title', 'reason', 'created', 'id', 'type', 'operator_name', 'product_title', 'quantity', 'bill_number']


class CashierStatsSerializer(serializers.ModelSerializer):
    cancelation_reasons = CancelationReasonSerializer(many=True, read_only=True)
    payment_groups = ListPaymentsGroupsSerializer(many=True, read_only=True)
    class Meta:
        model = Cashier
        fields = [
            'id',
            'open',
            'identifier',
            'initial_value',
            'opened_by_name',
            'closed_by_name',
            'created',
            'modified',
            'closed_at',
            'cancelation_reasons',
            'payment_groups',
        ]



