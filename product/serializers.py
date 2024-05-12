from rest_framework import serializers
from .models import *

class UnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Unit
        fields = '__all__'

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'




class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'category', 'price', 'unit', 'prod_code', 'quantity']
        read_only_fields = ['prod_code']  # prod_code should be generated in the backend

class ProductCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['name', 'description', 'category', 'price', 'unit']
        # Exclude 'prod_code' and 'quantity' as they are read-only or auto-generated

class ProductUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['name', 'description', 'category', 'price', 'unit']
        read_only_fields = ['prod_code']  # prod_code should not be updated
    

                                                                    # INPUT
class ProductInputSerializer(serializers.ModelSerializer):
    user_id = serializers.HiddenField(default=serializers.CurrentUserDefault())
    class Meta:
        model = ProductInput
        fields = ['id', 'product', 'input_quantity', 'user_id', "created_at"]

    def create(self, validated_data):
        # Retrieve the current user from the request context
        user = self.context['request'].user
        
        # Set the current user as the user_id for the product input
        validated_data['user_id'] = user
        
        # Create and return the ProductInput instance
        return super().create(validated_data)
    
class ProductInputGetSerializer(serializers.ModelSerializer):
    product_name = serializers.SerializerMethodField()

    class Meta:
        model = ProductInput
        fields = ['id', 'product_name', 'all_quantity', 'input_quantity', 'user_id', 'created_at']

    def get_product_name(self, obj):
        if obj.product:
            return obj.product.name
        return None

                                                        # OUTPUT
class ProductOutputSerializer(serializers.ModelSerializer):
    user_id = serializers.HiddenField(default=serializers.CurrentUserDefault())
    class Meta:
        model = ProductOutput
        fields = ['id', 'product', 'output_quantity', 'user_id', "created_at"]

    def create(self, validated_data):
        # Retrieve the current user from the request context
        user = self.context['request'].user
        
        # Set the current user as the user_id for the product input
        validated_data['user_id'] = user
        
        # Create and return the ProductInput instance
        return super().create(validated_data)
    

class ProductOutputGetSerializer(serializers.ModelSerializer):
    product_name = serializers.SerializerMethodField()

    class Meta:
        model = ProductOutput
        fields = ['id', 'product_name', 'all_quantity', 'output_quantity', 'user_id', 'created_at']

    def get_product_name(self, obj):
        if obj.product:
            return obj.product.name
        return None