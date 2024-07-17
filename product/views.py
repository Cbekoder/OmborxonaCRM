from django.shortcuts import get_object_or_404
from drf_yasg import openapi
from rest_framework import status
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
# from rest_framework_simplejwt.authentication import JWTAuthentication
# from users.permissions import IsBuxgalterUser, IsOmborchiUser
from rest_framework.views import APIView
from django.http import Http404
from drf_yasg.utils import swagger_auto_schema
from .models import *
from users.models import ReportCode
import random
from .serializers import (CategorySerializer, UnitSerializer,
                          ProductSerializer, ProductOutputSerializer,
                          ProductInputSerializer, ProductInputGetSerializer,
                          ProductOutputGetSerializer, ProductCreateSerializer)


#### CATEGORY ####
class CategoriesAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(tags=['Categories'])
    def get(self, request):
        categories = Category.objects.all()
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data, status=200)

    @swagger_auto_schema(tags=['Categories'], request_body=CategorySerializer)
    def post(self, request):
        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors)


class CategoryAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, c):
        """
        Helper method to get the object with the given pk.
        Raises a 404 error if the object does not exist.
        """
        try:
            return Category.objects.get(pk=c)
        except Category.DoesNotExist:
            raise NotFound(detail="Category not found.")

    @swagger_auto_schema(tags=['Categories'])
    def get(self, request, c, *args, **kwargs):
        """
        Retrieve a category by its pk.
        """
        category = self.get_object(c)
        serializer = CategorySerializer(category)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(tags=['Categories'], request_body=CategorySerializer)
    def put(self, request, c, *args, **kwargs):

        category = self.get_object(c)
        serializer = CategorySerializer(category, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(tags=['Categories'], responses={204: 'No Content'})
    def delete(self, request, c, *args, **kwargs):
        category = self.get_object(c)
        category.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


#### UNITS ####
class UnitsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(tags=['Units'])
    def get(self, request):
        """
        List all units.
        """
        units = Unit.objects.all()
        serializer = UnitSerializer(units, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(tags=['Units'], request_body=UnitSerializer)
    def post(self, request):
        """
        Create a new unit.
        """
        serializer = UnitSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UnitAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, u):
        """
        Helper method to get the object with the given pk.
        Raises a 404 error if the object does not exist.
        """
        try:
            return Unit.objects.get(pk=u)
        except Unit.DoesNotExist:
            raise NotFound(detail="Unit not found.")

    @swagger_auto_schema(tags=['Units'])
    def get(self, request, u, *args, **kwargs):
        """
        Retrieve a unit by its pk.
        """
        unit = self.get_object(u)
        serializer = UnitSerializer(unit)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(tags=['Units'], request_body=UnitSerializer)
    def put(self, request, u, *args, **kwargs):
        """
        Update a unit by its pk.
        """
        unit = self.get_object(u)
        serializer = UnitSerializer(unit, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(tags=['Units'], responses={204: 'No Content'})
    def delete(self, request, u, *args, **kwargs):
        unit = self.get_object(u)
        unit.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


#### PRODUCTS ####
class ProductsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        tags=['Products'],
        manual_parameters=[
            openapi.Parameter('prod_code', openapi.IN_QUERY, description="Product Code", type=openapi.TYPE_STRING),
            openapi.Parameter('is_deleted', openapi.IN_QUERY, description="O'chirilgan mahsulotlarni ham qabul qilish",
                              type=openapi.TYPE_BOOLEAN),
            # openapi.Parameter('prod_id', openapi.IN_QUERY, description="Product ID", type=openapi.TYPE_INTEGER)
        ]
    )
    def get(self, request):
        prod_code = request.query_params.get('prod_code')
        is_deleted = request.query_params.get('is_deleted')

        if prod_code:
            product = get_object_or_404(Product, prod_code=prod_code)
            serializer = ProductSerializer(product)
            return Response(serializer.data, status=status.HTTP_200_OK)

        if is_deleted:
            products = Product.objects.all()
        else:
            products = Product.objects.filter(is_deleted=False)

        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(tags=['Products'], request_body=ProductCreateSerializer)
    def post(self, request):
        serializer = ProductCreateSerializer(data=request.data)
        barcode_number = self.generate_unique_ean13_barcode_number()
        if serializer.is_valid():
            serializer.validated_data['prod_code'] = barcode_number
            serializer.validated_data['quantity'] = 0
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors)

    def generate_unique_ean13_barcode_number(self, max_attempts=100):
        for _ in range(max_attempts):
            barcode_number = self.generate_ean13_barcode_number()
            if not Product.objects.filter(prod_code=barcode_number).exists():
                return str(barcode_number)
        raise Exception("Failed to generate a unique EAN-13 barcode number after max attempts")

    def generate_ean13_barcode_number(self):
        first_12_digits = ''.join([str(random.randint(0, 9)) for _ in range(12)])
        check_digit = self._calculate_ean13_check_digit(first_12_digits)
        ean13_barcode_number = first_12_digits + str(check_digit)
        return str(ean13_barcode_number)

    def _calculate_ean13_check_digit(self, first_12_digits):
        odd_sum = sum(int(digit) for digit in first_12_digits[::2])
        even_sum = sum(int(digit) for digit in first_12_digits[1::2]) * 3
        total_sum = odd_sum + even_sum
        check_digit = (10 - (total_sum % 10)) % 10
        return check_digit


class ProductAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, p):
        """
        Helper method to get the object with the given pk.
        Raises a 404 error if the object does not exist.
        """
        try:
            return Product.objects.get(pk=p)
        except Product.DoesNotExist:
            raise NotFound(detail="Product not found.")

    @swagger_auto_schema(tags=['Products'])
    def get(self, request, p):
        product = self.get_object(p)
        serializer = ProductSerializer(product)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(tags=['Products'], request_body=ProductSerializer)
    def put(self, request, p, *args, **kwargs):
        product = self.get_object(p)
        serializer = ProductSerializer(product, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(tags=['Products'], request_body=ProductSerializer)
    def patch(self, request, p, *args, **kwargs):
        product = self.get_object(p)
        serializer = ProductSerializer(product, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(tags=['Products'], responses={204: 'No Content'})
    def delete(self, request, p, *args, **kwargs):
        product = self.get_object(p)
        product.is_deleted = True
        product.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


# class ProductByCode(APIView):
#     permission_classes = [IsAuthenticated,]
#     @swagger_auto_schema(tags=['Products'])
#     def get(self, request, prod_code):
#         if not prod_code:
#             return Response({"Xabar": "Maxsulot kodi berilmadi"}, status=status.HTTP_400_BAD_REQUEST)
#         product = get_object_or_404(Product, prod_code=str(prod_code))
#         serializer = ProductSerializer(product)
#         return Response(serializer.data, status=status.HTTP_200_OK)


#### INPUT OUTPUT ####
class ProductInputsAPIView(APIView):
    """
    List all product inputs or create a new one.
    """
    permission_classes = [IsAuthenticated, ]

    @swagger_auto_schema(tags=['Product-Input-Output'], request_body=ProductInputSerializer)
    def post(self, request):
        serializer = ProductInputSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            product_id = serializer.validated_data['product'].id
            input_quantity = serializer.validated_data['input_quantity']
            user_id = request.user.id
            if input_quantity:
                product_input = serializer.save(user_id=user_id)
                product = Product.objects.get(pk=product_id)
                product.quantity += input_quantity

                product.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response({"Xabar": "Noto'g'ri miqdor!"}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProductOutputAPIView(APIView):
    permission_classes = [IsAuthenticated, ]
    """
    List all product inputs or create a new one.
    """

    @swagger_auto_schema(tags=['Product-Input-Output'], request_body=ProductOutputSerializer)
    def post(self, request):
        serializer = ProductOutputSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            product_id = serializer.validated_data['product'].id
            output_quantity = serializer.validated_data['output_quantity']
            user_id = request.user.id

            # Create the ProductInput instance
            if output_quantity <= Product.objects.get(pk=product_id).quantity:
                product_output = serializer.save(user_id=user_id)
                product = Product.objects.get(pk=product_id)
                product.quantity -= output_quantity
                product.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response({"Xabar": "Noto'g'ri miqdor!"}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
