from rest_framework import viewsets, status, generics
from rest_framework.response import Response
from .models import *
import random
from .serializers import (CategorySerializer, UnitSerializer,
                          ProductSerializer, ProductOutputSerializer,
                          ProductInputSerializer)


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class UnitViewSet(viewsets.ModelViewSet):
    queryset = Unit.objects.all()
    serializer_class = UnitSerializer



class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def perform_create(self, serializer):
        # Generate EAN-13 barcode number
        barcode_number = self.generate_unique_ean13_barcode_number()
        
        # Set the barcode number and default quantity in the serializer data
        serializer.validated_data['prod_code'] = barcode_number
        serializer.validated_data['quantity'] = 0
        
        # Save the product
        serializer.save()

    def generate_unique_ean13_barcode_number(self, max_attempts=100):
        for _ in range(max_attempts):
            barcode_number = self.generate_ean13_barcode_number()
            if not Product.objects.filter(prod_code=barcode_number).exists():
                return barcode_number
        raise Exception("Failed to generate a unique EAN-13 barcode number after max attempts")

    def generate_ean13_barcode_number(self):
        # Generate the first 12 digits (excluding the last check digit)
        first_12_digits = ''.join([str(random.randint(0, 9)) for _ in range(12)])
        
        # Calculate the check digit
        check_digit = self._calculate_ean13_check_digit(first_12_digits)
        
        # Concatenate the first 12 digits with the check digit
        ean13_barcode_number = first_12_digits + str(check_digit)
        
        return ean13_barcode_number

    def _calculate_ean13_check_digit(self, first_12_digits):
        # Calculate the check digit using the EAN-13 algorithm
        odd_sum = sum(int(digit) for digit in first_12_digits[::2])
        even_sum = sum(int(digit) for digit in first_12_digits[1::2]) * 3
        total_sum = odd_sum + even_sum
        check_digit = (10 - (total_sum % 10)) % 10
        
        return check_digit
    

class ProductInputCreateAPIView(generics.CreateAPIView):
    serializer_class = ProductInputSerializer

    def perform_create(self, serializer):
        # Add input quantity to the product quantity
        product_id = serializer.validated_data['product'].id
        input_quantity = serializer.validated_data['input_quantity']
        product = Product.objects.get(pk=product_id)
        product.quantity += input_quantity
        product.save()


class ProductOutputCreateAPIView(generics.CreateAPIView):
    serializer_class = ProductOutputSerializer

    def perform_create(self, serializer):
        # Remove output quantity from the product quantity
        product_id = serializer.validated_data['product'].id
        output_quantity = serializer.validated_data['output_quantity']
        product = Product.objects.get(pk=product_id)
        if product.quantity < output_quantity:
            return Response({"error": "Not enough quantity available"}, status=status.HTTP_400_BAD_REQUEST)
        product.quantity -= output_quantity
        product.save()

        # Create ProductOutput instance
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)

class ProductInputAPIView(generics.ListAPIView):
    serializer_class = ProductInputSerializer

    def get_queryset(self):
        return ProductInput.objects.all()

class ProductOutputAPIView(generics.ListAPIView):
    serializer_class = ProductOutputSerializer

    def get_queryset(self):
        return ProductOutput.objects.all()