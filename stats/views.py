from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from django.http import JsonResponse
from django.utils.timezone import make_aware
from datetime import datetime
from django.db.models import Sum
from rest_framework.views import APIView
from rest_framework import status
from django.db.models import Q
from rest_framework_simplejwt.authentication import JWTAuthentication

from product.models import Product, ProductInput, ProductOutput
from product.serializers import ProductInputGetSerializer, ProductOutputGetSerializer
from users.models import ReportCode
from .serializers import ReportSerializer
from rest_framework.response import Response

#### INPUT STATS ####
class ProductInputsListAPIView(APIView):
    """
    List all product inputs or create a new one.
    """
    permission_classes = [IsAuthenticated, ]
    @swagger_auto_schema(tags=['Statistics'])
    def get(self, request):
        paginator = PageNumberPagination()
        paginator.page_size = 10

        product_inputs = ProductInput.objects.all()
        result_page = paginator.paginate_queryset(product_inputs, request)
        serializer = ProductInputGetSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)

class ProductInputListByProduct(APIView):
    permission_classes = [IsAuthenticated,]
    @swagger_auto_schema(tags=['Statistics'])
    def get(self, request, product_id, format=None):
        # Filter inputs by the specified product_id
        product_inputs = ProductInput.objects.filter(product_id=product_id)
        paginator = PageNumberPagination()
        paginator.page_size = 10
        result_page = paginator.paginate_queryset(product_inputs, request)
        serializer = ProductInputGetSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)


#### OUTPUTS ####
class ProductOutputsListAPIView(APIView):
    """
    List all product inputs or create a new one.
    """
    permission_classes = [IsAuthenticated, ]
    @swagger_auto_schema(tags=['Statistics'])
    def get(self, request):
        paginator = PageNumberPagination()
        paginator.page_size = 10
        product_outputs = ProductOutput.objects.all()
        result_page = paginator.paginate_queryset(product_outputs, request)
        serializer = ProductOutputGetSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)

class ProductOutputListByProduct(APIView):
    permission_classes = [IsAuthenticated, ]
    """
    Retrieve all inputs for a specific product.
    """
    @swagger_auto_schema(tags=['Statistics'])

    def get(self, request, product_id, format=None):
        # Filter inputs by the specified product_id
        product_output = ProductOutput.objects.filter(product_id=product_id)
        paginator = PageNumberPagination()
        paginator.page_size = 10
        result_page = paginator.paginate_queryset(product_output, request)
        serializer = ProductOutputGetSerializer(result_page, many=True)

        return paginator.get_paginated_response(serializer.data)


#### REPORT ####
class ReportAPIView(APIView):
    serializer_class = ReportSerializer
    authentication_classes = [JWTAuthentication]
    @swagger_auto_schema(tags=['Statistics'])
    def get(self, request, *args, **kwargs):
        token = request.headers.get('Authorization')
        password = request.headers.get('password')

        if token:
            report_data = self.get_report_with_token(request)
            return Response(report_data)
        elif password:
            report_data = self.get_report_with_password(password)
            return Response(report_data)
        else:
            return JsonResponse({'error': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)

    def get_report_with_token(self, request):
        date_str = request.GET.get('date')
        start_date_str = request.GET.get('start_date')
        end_date_str = request.GET.get('end_date')
        category_id = request.GET.get('category')
        order_by = request.GET.get('order_by')
        search_query = request.GET.get('search')

        products = Product.objects.all()

        # Filtering by category
        if category_id:
            products = products.filter(category_id=category_id)

        if search_query:
            products = products.filter(
                Q(prod_code__icontains=search_query) |
                Q(name__icontains=search_query) |
                Q(category__name__icontains=search_query)
            )

        # Ordering
        if order_by:
            if order_by == 'category':
                products = products.order_by('category__name')
            elif order_by == 'name':
                products = products.order_by('name')
            elif order_by == 'price':
                products = products.order_by('price')
            elif order_by == 'quantity':
                products = products.order_by('quantity')

        # Fetching report data based on date range
        if date_str:
            try:
                date = make_aware(datetime.strptime(date_str, '%Y-%m-%d'))
                products = products.filter(
                    productinput__created_at__date=date,
                    productoutput__created_at__date=date
                )
            except ValueError:
                return {'error': 'Invalid date format'}

        elif start_date_str and end_date_str:
            try:
                start_date = make_aware(datetime.strptime(start_date_str, '%Y-%m-%d'))
                end_date = make_aware(datetime.strptime(end_date_str, '%Y-%m-%d'))
                products = products.filter(
                    productinput__created_at__range=(start_date, end_date),
                    productoutput__created_at__range=(start_date, end_date)
                )
            except ValueError:
                return {'error': 'Invalid date format'}

        report_data = self.generate_report_data(products)
        return report_data

    def get_report_with_password(self, password):
        last_password = ReportCode.objects.last().password
        if password == last_password:
            products = Product.objects.all()
            report_data = self.generate_report_data(products)
            return report_data
        else:
            return {'error': 'Invalid password'}

    def generate_report_data(self, products):
        report_data = []

        for product in products:
            goods_in = ProductInput.objects.filter(product=product)
            goods_out = ProductOutput.objects.filter(product=product)

            goods_in_quantity = goods_in.aggregate(goods_in_quantity=Sum('input_quantity'))['goods_in_quantity'] or 0
            goods_in_price = goods_in_quantity * product.price

            goods_out_quantity = goods_out.aggregate(goods_out_quantity=Sum('output_quantity'))['goods_out_quantity'] or 0
            goods_out_price = goods_out_quantity * product.price

            beginning_quantity = product.quantity or 0
            beginning_price = beginning_quantity * product.price if beginning_quantity else 0

            last_quantity = beginning_quantity + goods_in_quantity - goods_out_quantity
            last_price = beginning_price + goods_in_price - goods_out_price

            if all(value == 0 for value in [
                beginning_quantity, beginning_price, goods_in_quantity, goods_in_price,
                goods_out_quantity, goods_out_price, last_quantity, last_price
            ]):
                continue

            product_report = {
                'product_name': product.name,
                'product_code': product.prod_code,
                'product_unit': product.unit.name,
                'first_quantity': beginning_quantity,
                'first_price': beginning_price,
                'in_quantity': goods_in_quantity,
                'in_price': goods_in_price,
                'out_quantity': goods_out_quantity,
                'out_price': goods_out_price,
                'last_quantity': last_quantity,
                'last_price': last_price,
            }
            report_data.append(product_report)

        return report_data
