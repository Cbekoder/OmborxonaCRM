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
    category = serializers.SerializerMethodField()
    unit = serializers.SerializerMethodField()
    quantity = serializers.IntegerField(read_only=True)  # Make quantity read-only

    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'category', 'price', 'unit', 'prod_code', 'quantity']
        read_only_fields = ['prod_code']  # prod_code should be generated in the backend

    def get_category(self, obj):
        if obj.category:
            return obj.category.name
        return None

    def get_unit(self, obj):
        if obj.unit:
            return obj.unit.name
        return None
    
class ProductInputSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductInput
        fields = ['id', 'product', 'input_quantity', 'user_id']

class ProductOutputSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductOutput
        fields = ['id', 'product', 'output_quantity', 'user_id']
