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
        fields = ['id', 'name', 'description', 'category', 'price', 'unit', 'prod_code', 'quantity', 'is_deleted']
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


class ProductDetailInputOutputSerializer(serializers.ModelSerializer):
    unit = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField()
    class Meta:
        model = Product
        fields = ['name', 'prod_code', 'unit', 'category', 'price']

    def get_unit(self, obj):
        return obj.unit.name

    def get_category(self, obj):
        return obj.category.name
# INPUT


class ProductInputSerializer(serializers.ModelSerializer):
    user_id = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = ProductInput
        fields = ['id', 'product', 'input_quantity', "created_at", 'user_id']

    def create(self, validated_data):
        # Retrieve the current user from the request context
        user = self.context['request'].user

        # Set the current user as the user_id for the product input
        validated_data['user_id'] = user

        # Create and return the ProductInput instance
        return super().create(validated_data)


class ProductInputGetSerializer(serializers.ModelSerializer):
    product = ProductDetailInputOutputSerializer()
    user = serializers.SerializerMethodField()

    class Meta:
        model = ProductInput
        fields = ['id', 'product', 'input_quantity', 'user', 'created_at']

    def get_product_name(self, obj):
        if obj.product:
            return obj.product.name
        return None

    def get_user(self, obj):
        return obj.user_id.first_name + ' ' + obj.user_id.last_name
        # return obj.user_id.username

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
    product = ProductDetailInputOutputSerializer()
    user = serializers.SerializerMethodField()

    class Meta:
        model = ProductOutput
        fields = ['id', 'product', 'output_quantity', 'user', 'created_at']

    def get_user(self, obj):
        return obj.user_id.first_name + ' ' + obj.user_id.last_name

class CombinedProductSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    type = serializers.CharField()
    product = serializers.CharField(source='product.name', allow_null=True)
    quantity = serializers.DecimalField(max_digits=8, decimal_places=2)
    all_quantity = serializers.DecimalField(max_digits=8, decimal_places=2)
    created_at = serializers.DateTimeField()
    user_id = serializers.PrimaryKeyRelatedField(read_only=True)
