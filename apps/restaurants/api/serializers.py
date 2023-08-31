
from rest_framework import serializers

from apps.user.models import User
from apps.financial.models import Bill
from apps.restaurants.models import( 
    Printer,
    Product,
    ProductPrice, 
    Restaurant, 
    RestauratCategory,
    Employer,
    ProductCategory,
    ProductComplementCategory,
    ProductComplementItem,
    Sidebar,
    Table,
    Catalog,
    ComplementPrice,
)
from django.db import transaction
from apps.user.api.serializers import UserSerializer
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = RestauratCategory
        fields = ['id', 'title', 'description', 'slug']

class RestaurantSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.id')
    url = serializers.HyperlinkedIdentityField(view_name='restaurant-detail')
    category_detail = serializers.SerializerMethodField(read_only=True)
    category = serializers.PrimaryKeyRelatedField(queryset=RestauratCategory.objects.all(), write_only=True) 

    class Meta:
        model = Restaurant
        fields = ['id', 'owner', 'url', 'category', 'category_detail', 
                    'email',
                    'slug',
                    'title',
                    'description',
                    'phone',
                    'zip_code',
                    'state',
                    'city',
                    'street',
                    'number',
                    'complement',
                    'photo',
                    'open',
                ]

    def get_category_detail(self, obj):
        category = obj.category
        serializer = CategorySerializer(category)
        return serializer.data

    def validate(self, data):
        if self.context['request'].user.is_superuser:
            return data
        if 'owner' in data and self.context['request'].user.username != data['owner']:
            raise serializers.ValidationError({"detail":"You are not the owner of this restaurant."})
        return data

    def create(self, validated_data):
        validated_data['owner'] = self.context['request'].user
        return Restaurant.objects.create(**validated_data)
    
    def update(self, instance, validated_data):
        validated_data['owner'] = self.context['request'].user
        return super().update(instance, validated_data)
    
    def list(self, request):
        if request.user.is_superuser:
            return super().list(request)
        return super().list(request).filter(owner=request.user)
    

    
class EmployerSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='employer-detail')
    email = serializers.CharField(source='user.email')
    password = serializers.CharField(source='user.password', write_only=True)
    first_name = serializers.CharField(source='user.first_name')
    last_name = serializers.CharField(source='user.last_name')

    class Meta:
        model = Employer
        fields = '__all__'
        read_only_fields = ('user', 'restaurant')

    @transaction.atomic
    def create(self, validated_data):
        user_data = validated_data.pop('user')
        try:
            user = User.objects.create_user(
                username=user_data['email'],
                email=user_data['email'],
                password=user_data['password'],
                first_name=user_data.get('first_name'),
                last_name=user_data.get('last_name')
            )
        except Exception as e:
            raise serializers.ValidationError({"detail": str(e)})
        restaurant = Restaurant.objects.filter(owner=self.context['request'].user).first()

        if restaurant is not None:
            employer = Employer.objects.create(user=user, restaurant=restaurant, **validated_data)
            return employer

        raise serializers.ValidationError({"detail":"The user is not an owner of any restaurant."})
    
    @transaction.atomic
    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', None)
        if user_data:
            user = instance.user
            user.email = user_data.get('email', user.email)
            user.password = user_data.get('password', user.password)
            user.first_name = user_data.get('first_name', user.first_name)
            user.last_name = user_data.get('last_name', user.last_name)
            user.save()

        return super().update(instance, validated_data)


class ProductCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductCategory
        fields = '__all__'
        read_only_fields = ('restaurant',)


class PrinterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Printer
        fields = '__all__'
        read_only_fields = ('restaurant',)

    def create(self, validated_data):
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
        validated_data['restaurant'] = restaurant
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
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
        validated_data['restaurant'] = restaurant
        return super().update(instance, validated_data)

class PrinterDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Printer
        fields = ['id', 'name']
class ProductSerializer(serializers.ModelSerializer):
    category = ProductCategorySerializer(source='product_category', read_only=True)
    printer_detail = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = Product
        fields = '__all__'

    def get_printer_detail(self, obj):
        printer = obj.printer
        serializer = PrinterDetailSerializer(printer)
        return serializer.data

class ProductComplementItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductComplementItem
        fields = [
            'id',
            'title',
            'order',
            'price',
            'min_value',
            'max_value',
        ]


class ProductComplementSerializer(serializers.ModelSerializer):
    complement_items = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = ProductComplementCategory
        fields = ['id', 'title', 'order', 'active', 'input_type', 'business_rules', 'max_value', 'min_value', 'products', 'complement_items', 'restaurant']
        read_only_fields = ('restaurant',)
    def get_complement_items(self, obj):
        items = obj.complement_items.filter(active=True)
        serializer = ProductComplementItemSerializer(items, many=True)
        return serializer.data
    
    def save(self, **kwargs):
        if self.instance is None:
            try:
                restaurant = Restaurant.objects.get(owner=self.context['request'].user)
            except Restaurant.DoesNotExist:
                restaurant = None
                try:
                    employer = Employer.objects.get(user=self.context['request'].user)
                    restaurant = employer.restaurant
                except Employer.DoesNotExist:
                    raise serializers.ValidationError({"detail":"Este usuário não é funcionário de nenhum restaurante."})
            self.validated_data['restaurant'] = restaurant
        return super().save(**kwargs)
    

class BillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bill
        fields = ['id', 'number', 'open', 'client_name', 'created']

class TableSerializer(serializers.ModelSerializer):
    bills = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = Table
        fields = '__all__'
        read_only_fields = ('restaurant',)

    def get_bills(self, obj):
        bills = obj.bills.filter(open=True)
        serializer = BillSerializer(bills, many=True)
        return serializer.data

    def create(self, validated_data):
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
        validated_data['restaurant'] = restaurant
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
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
        validated_data['restaurant'] = restaurant
        return super().update(instance, validated_data)


class SidebarSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sidebar
        fields = ['id', 'title']

class UserPermissionsSerializer(serializers.ModelSerializer):
    sidebar_permissions = SidebarSerializer(many=True, read_only=True)
    user = UserSerializer(read_only=True)
    class Meta:
        model = Employer
        fields = ['id', 'sidebar_permissions', 'role', 'office', 'user']

    

class ProductCategoryCatalogSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductCategory
        fields = [
            'id',
            'title',
        ]


class ProductCatalogSerializer(serializers.ModelSerializer):
    product_category = ProductCategoryCatalogSerializer(read_only=True)
    complement_categories = ProductComplementSerializer(many=True, read_only=True)
    class Meta:
        model = Product
        fields = [
            "id",    
            "title",
            "description",
            "price",
            "listed",
            "type_of_sale",
            "codigo_produto",
            'photo',
            "product_category",
            "complement_categories"
        ]

class ProductComplementPriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ComplementPrice
        fields = [
            'id',
            'price',
            'product_complement_item',
        ]

class ProductPriceSerializer(serializers.ModelSerializer):
    product = ProductCatalogSerializer(read_only=True)
    class Meta:
        model = ProductPrice
        fields = [
            'id',
            'price',
            'product',
        ]
class CatalogSerializer(serializers.ModelSerializer):
    products_prices = serializers.SerializerMethodField(read_only=True)
    complement_prices = ProductComplementPriceSerializer(many=True, read_only=True)
    class Meta:
        model = Catalog
        fields = [
            'id',
            'title',
            'description',
            'slug',
            'photo',
            'delivery',
            'complement_prices',
            'products_prices',
        ]

    def get_products_prices(self, obj):
        product_prices = obj.products_prices.filter(product__active=True, product__product_category__active=True, product__product_category__restaurant__active=True).order_by('product__product_category__order', 'product__product_category__title','product__order', 'product__title')
        serializer = ProductPriceSerializer(product_prices, many=True)
        return serializer.data
    

class CatalogInRestaurantSerializer(serializers.ModelSerializer):
    class Meta: 
        model = Catalog
        fields = [
            'id',
            'title',
            'description',
            'slug',
            'photo',
            'delivery',
        ]
class RestaurantCatalogSerializer(serializers.ModelSerializer):
    catalogs = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = Restaurant
        fields = [
            'id',
            'title',
            'description',
            'open',
            'open_time',
            'close_time',
            'slug',
            'photo',
            'phone',
            'zip_code',
            'state',
            'city',
            'street',
            'number',
            'complement',
            'catalogs',
        ]

    def get_catalogs(self, obj):
        catalogs = obj.catalogs.filter(active=True).order_by('order', 'title')
        serializer = CatalogInRestaurantSerializer(catalogs, many=True)
        return serializer.data