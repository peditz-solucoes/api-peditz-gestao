from rest_framework import serializers
from apps.user.models import User

from ..models import Item, ItemCategory, ItemTransaction, ItemItem
from django.db import transaction

class ItemCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemCategory
        fields = ['title', 'id']


class IngredientInItemSerializer(serializers.ModelSerializer):
    item = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = ItemItem
        fields = ['id', 'item', 'quantity']

    def get_item(self, obj):
        return obj.ingredient.title

class ItemSerializer(serializers.ModelSerializer):
    category_detail = serializers.SerializerMethodField()
    category = serializers.CharField(write_only=True, required=False)
    ingredients = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = Item
        fields = [
            'title',
            'description',
            'barcode',
            'product_type',
            'minimum_stock',
            'stock',
            'id',
            'category_detail',
            'category',
            'ingredients',
        ]

    def get_ingredients(self, obj):
        return IngredientInItemSerializer(obj.items, many=True).data

    def get_category_detail(self, obj):
        return ItemCategorySerializer(obj.category).data
    
    @transaction.atomic
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

        try:
            category_data = ItemCategory.objects.get_or_create(title=validated_data['category'], restaurant=restaurant)
            validated_data['category'] = category_data[0]
        except ItemCategory.DoesNotExist:
            raise serializers.ValidationError({"detail":"Error ao criar categoria."})

        return super().create(validated_data)
    
class UserSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    class Meta:
        model = User
        fields = ['id', 'name']

    def get_name(self, obj):
        return obj.get_full_name()

class ItemStockTransactionSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    item_detail = serializers.SerializerMethodField()

    class Meta:
        model = ItemTransaction
        fields = '__all__'
        read_only_fields = ['user', 'user_name']

    def get_item_detail(self, obj):
        return ItemSerializer(obj.item).data

    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['user'] = user
        try:
            return super().create(validated_data)
        except Exception as e:
            raise serializers.ValidationError({"detail":str(e)})
        
    
class ItemIngredientListSerializer(serializers.ModelSerializer):
    class  Meta:
        model = Item
        fields = ['id', 'title']

class ItemIngredientSerializer(serializers.ModelSerializer):
    item_detail = serializers.SerializerMethodField(read_only=True)
    ingredient_detail = serializers.SerializerMethodField(read_only=True)
    item = serializers.PrimaryKeyRelatedField(queryset=Item.objects.all(), write_only=True)
    ingredient = serializers.PrimaryKeyRelatedField(queryset=Item.objects.all(), write_only=True)
    class Meta:
        model = ItemItem
        fields = [
            'id',
            'item',
            'ingredient',
            'quantity',
            'item_detail',
            'ingredient_detail',
        ]

    def get_item_detail(self, obj):
        return ItemIngredientListSerializer(obj.item).data
    
    def get_ingredient_detail(self, obj):
        return ItemIngredientListSerializer(obj.ingredient).data
    
    def create(self, validated_data):
        if validated_data.get('item', None) is not None and validated_data.get('ingredient', None) is not None:
            if validated_data.get('item', None) == validated_data.get('ingredient', None):
                raise serializers.ValidationError({"detail":"Um item não pode ser ingrediente dele mesmo."})
            if ItemItem.objects.filter(item=validated_data.get('item', None), ingredient=validated_data.get('ingredient', None)).exists():
                raise serializers.ValidationError({"detail":"Este ingrediente já existe neste item"})
            if ItemItem.objects.filter(item=validated_data.get('ingredient', None), ingredient=validated_data.get('item', None)).exists():
                raise serializers.ValidationError({"detail":"Você não pode adicionar este item como ingrediente, pois ele já é um ingrediente do item selecionado."})
        return super().create(validated_data)