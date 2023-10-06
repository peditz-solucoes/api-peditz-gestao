from decimal import Decimal
import json
import os
import requests
from rest_framework import serializers

from apps.restaurants.models import Employer, Product

from ..models import Item, ItemCategory
import pytz
from datetime import datetime
from django.db import transaction

class ItemCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemCategory
        fields = ['title', 'id']

class ItemSerializer(serializers.ModelSerializer):
    category_detail = serializers.SerializerMethodField()
    category = serializers.CharField(write_only=True, required=False)
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
        ]

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