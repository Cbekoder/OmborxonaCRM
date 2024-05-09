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
    
class ProductInputSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductInput
        fields = ['id', 'product', 'input_quantity', 'user_id']

class ProductOutputSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductOutput
        fields = ['id', 'product', 'output_quantity', 'user_id']
