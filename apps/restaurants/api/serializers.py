
from rest_framework import serializers

from apps.restaurants.models import Restaurant, RestauratCategory


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
            raise serializers.ValidationError("You are not the owner of this restaurant.")
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
    
