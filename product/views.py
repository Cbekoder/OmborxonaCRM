from rest_framework import viewsets, status, generics
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from users.permissions import IsBuxgalterUser, IsOmborchiUser
from rest_framework.views import APIView
from django.http import Http404
from .models import *
from users.models import ReportCode
import random
from .serializers import (CategorySerializer, UnitSerializer,
                          ProductSerializer, ProductOutputSerializer,
                          ProductInputSerializer, ProductInputGetSerializer,
                          ProductOutputGetSerializer, ProductCreateSerializer)


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
            # Generate a new EAN-13 barcode number
            barcode_number = self.generate_ean13_barcode_number()

            # Check if the generated barcode number already exists
            if not Product.objects.filter(prod_code=barcode_number).exists():
                return str(barcode_number)

        # If max_attempts reached without finding a unique barcode number, raise an exception or handle the situation
        raise Exception("Failed to generate a unique EAN-13 barcode number after max attempts")

    def generate_ean13_barcode_number(self):
        # Generate the first 12 digits (excluding the last check digit)
        first_12_digits = ''.join([str(random.randint(0, 9)) for _ in range(12)])

        # Calculate the check digit
        check_digit = self._calculate_ean13_check_digit(first_12_digits)

        # Concatenate the first 12 digits with the check digit
        ean13_barcode_number = first_12_digits + str(check_digit)

        return str(ean13_barcode_number)

    def _calculate_ean13_check_digit(self, first_12_digits):
        # Calculate the check digit using the EAN-13 algorithm
        odd_sum = sum(int(digit) for digit in first_12_digits[::2])
        even_sum = sum(int(digit) for digit in first_12_digits[1::2]) * 3
        total_sum = odd_sum + even_sum
        check_digit = (10 - (total_sum % 10)) % 10

        return check_digit

#     queryset = ProductInput.objects.all()
#     serializer_class = ProductInputSerializer

#     def get(self, request, *args, **kwargs):
#         if 'pk' in kwargs:
#             return self.retrieve(request, *args, **kwargs)
#         else:
#             return self.list(request, *args, **kwargs)

class ProductInputList(APIView):
    """
    List all product inputs or create a new one.
    """
    def get(self, request, format=None):
        product_inputs = ProductInput.objects.all()
        serializer = ProductInputGetSerializer(product_inputs, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ProductInputSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            product_id = serializer.validated_data['product'].id
            input_quantity = serializer.validated_data['input_quantity']
            user_id = request.user.id

            # Create the ProductInput instance
            if input_quantity:
                product_input = serializer.save(user_id=user_id)
                # Update the related Product instance
                product = Product.objects.get(pk=product_id)
                product.quantity += input_quantity
            
                product.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response({"Xabar": "Noto'g'ri miqdor!"}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ProductInputDetail(APIView):
    """
    Retrieve, update or delete a product input instance.
    """
    def get_object(self, pk):
        try:
            return ProductInput.objects.get(pk=pk)
        except ProductInput.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        product_input = self.get_object(pk)
        serializer = ProductInputGetSerializer(product_input)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        product_input = self.get_object(pk)
        serializer = ProductInputSerializer(product_input, data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # def delete(self, request, pk, format=None):
    #     product_input = self.get_object(pk)
    #     product = product_input.product
    #     product.quantity -=  product_input.input_quantity
    #     product.save()
    #     product_input.delete()
    #     return Response(status=status.HTTP_204_NO_CONTENT)
    

class ProductByCode(APIView):
    def get(self, request):
        prod_code = request.query_params.get('prod_code')
        if not prod_code:
            return Response({"Xabar": "Maxsulot kodi berilmadi"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            product = Product.objects.get(prod_code=prod_code)
        except Product.DoesNotExist:
            return Response({"Xabar": "Maxsulot topilmadi"}, status=status.HTTP_404_NOT_FOUND)
        serializer = ProductSerializer(product)
        return Response(serializer.data, status=status.HTTP_200_OK)

class ProductInputListByProduct(APIView):
    """
    Retrieve all inputs for a specific product.
    """

    def get(self, request, product_id, format=None):
        # Filter inputs by the specified product_id
        product_inputs = ProductInput.objects.filter(product_id=product_id)
        serializer = ProductInputGetSerializer(product_inputs, many=True)
        return Response(serializer.data)


                                                                            # OUTPUT
class ProductOutputList(APIView):
    """
    List all product inputs or create a new one.
    """
    def get(self, request, format=None):
        product_outputs = ProductOutput.objects.all()
        serializer = ProductOutputGetSerializer(product_outputs, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ProductOutputSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            product_id = serializer.validated_data['product'].id
            output_quantity = serializer.validated_data['output_quantity']
            user_id = request.user.id

            # Create the ProductInput instance
            if output_quantity <= Product.objects.get(pk=product_id).quantity:
                product_output = serializer.save(user_id=user_id)
                # Update the related Product instance
                product = Product.objects.get(pk=product_id)
                product.quantity -= output_quantity
                product.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response({"Xabar": "Noto'g'ri miqdor!"}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProductOutputtDetail(APIView):
    """
    Retrieve, update or delete a product input instance.
    """
    def get_object(self, pk):
        try:
            return ProductOutput.objects.get(pk=pk)
        except ProductOutput.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        product_output = self.get_object(pk)
        serializer = ProductOutputSerializer(product_output)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        product_output = self.get_object(pk)
        serializer = ProductOutputSerializer(product_output, data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # def delete(self, request, pk, format=None):
    #     product_output = self.get_object(pk)
    #     product = product_output.product
    #     product.quantity -= product_output.output_quantity
    #     product.save()
    #     product_output.delete()
    #     return Response(status=status.HTTP_204_NO_CONTENT)
    

class ProductOutputListByProduct(APIView):
    """
    Retrieve all inputs for a specific product.
    """

    def get(self, request, product_id, format=None):
        # Filter inputs by the specified product_id
        product_output = ProductOutput.objects.filter(product_id=product_id)
        serializer = ProductOutputGetSerializer(product_output, many=True)
        return Response(serializer.data)


# class ProductOutputCreateAPIView(generics.CreateAPIView):
#     serializer_class = ProductOutputSerializer

#     def perform_create(self, serializer):
#         # Remove output quantity from the product quantity
#         product_id = serializer.validated_data['product'].id
#         output_quantity = serializer.validated_data['output_quantity']
#         product = Product.objects.get(pk=product_id)
#         if product.quantity < output_quantity:
#             return Response({"error": "Not enough quantity available"}, status=status.HTTP_400_BAD_REQUEST)
#         product.quantity -= output_quantity
#         product.save()

#         # Create ProductOutput instance
#         serializer.save()

#         return Response(serializer.data, status=status.HTTP_201_CREATED)


# class ProductInputAPIView(generics.ListAPIView):
#     serializer_class = ProductInputSerializer
#     authentication_classes = (JWTAuthentication,)

#     def get_queryset(self):
#         if isinstance(self.request.user, User):
#             return ProductInput.objects.all()

#         password = self.request.headers.get('password')
#         report_code = ReportCode.objects.last()
#         if report_code and password == report_code.password:
#             return ProductInput.objects.all()
#         else:
#             return None

#     def list(self, request, *args, **kwargs):
#         queryset = self.get_queryset()
#         if queryset is None:
#             return Response("Error: Not allowed", status=status.HTTP_405_METHOD_NOT_ALLOWED)
#         serializer = self.get_serializer(queryset, many=True)
#         return Response(serializer.data)


# class ProductOutputAPIView(generics.ListAPIView):
#     serializer_class = ProductOutputSerializer
#     authentication_classes = (JWTAuthentication,)

#     def get_queryset(self):
#         if isinstance(self.request.user, User):
#             return ProductOutput.objects.all()
#         password = self.request.headers.get('password')
#         report_code = ReportCode.objects.last()
#         if report_code and password == report_code.password:
#             return ProductOutput.objects.all()
#         else:
#             return None

#     def list(self, request, *args, **kwargs):
#         queryset = self.get_queryset()
#         if queryset is None:
#             return Response("Error: Not allowed", status=status.HTTP_405_METHOD_NOT_ALLOWED)
#         serializer = self.get_serializer(queryset, many=True)
#         return Response(serializer.data)
