from rest_framework import viewsets, status, generics
from rest_framework.response import Response
from .models import *
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

class ProductInputCreateAPIView(generics.CreateAPIView):
    serializer_class = ProductInputSerializer

    def perform_create(self, serializer):
        # Add input quantity to the product quantity
        product_id = serializer.validated_data['product'].id
        input_quantity = serializer.validated_data['input_quantity']
        product = Product.objects.get(pk=product_id)
        product.quantity += input_quantity
        product.save()

        # Create ProductInput instance
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)


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