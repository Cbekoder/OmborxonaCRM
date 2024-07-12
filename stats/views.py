from django.shortcuts import get_object_or_404
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from django.http import JsonResponse
from django.utils.timezone import make_aware
from datetime import datetime
from django.db.models import Sum, F
from rest_framework.views import APIView
from rest_framework import status
from django.db.models import Q
from rest_framework_simplejwt.authentication import JWTAuthentication

from product.models import Product, ProductInput, ProductOutput
from product.serializers import ProductInputGetSerializer, ProductOutputGetSerializer, CombinedProductSerializer
from users.models import ReportCode
from .serializers import ReportSerializer
from rest_framework.response import Response

#### INPUT STATS ####
class ProductInputsListAPIView(APIView):
    """
    List all product inputs or create a new one.
    """
    permission_classes = [IsAuthenticated, ]

    @swagger_auto_schema(tags=['Statistics'], manual_parameters=[
        openapi.Parameter('product_id', openapi.IN_QUERY, description="Filter by product ID", type=openapi.TYPE_INTEGER),
    ])
    def get(self, request):
        product_inputs = ProductInput.objects.all()

        # Filter by product_id if provided in query parameters
        product_id = request.query_params.get('product_id')
        if product_id:
            product_inputs = product_inputs.filter(product_id=product_id)

        serializer = ProductInputGetSerializer(product_inputs, many=True)
        return Response(serializer.data)


#### OUTPUTS ####

class ProductOutputsListAPIView(APIView):
    """
    List all product outputs or create a new one.
    """
    permission_classes = [IsAuthenticated, ]

    @swagger_auto_schema(tags=['Statistics'], manual_parameters=[
        openapi.Parameter('product_id', openapi.IN_QUERY, description="Filter by product ID", type=openapi.TYPE_INTEGER),
    ])
    def get(self, request):
        product_outputs = ProductOutput.objects.all()

        # Filter by product_id if provided in query parameters
        product_id = request.query_params.get('product_id')
        if product_id:
            product_outputs = product_outputs.filter(product_id=product_id)

        serializer = ProductOutputGetSerializer(product_outputs, many=True)
        return Response(serializer.data)


class CombinedProductListAPIView(APIView):
    """
    List all product inputs and outputs, optionally filtered by product_id, ordered by datetime.
    """
    permission_classes = [IsAuthenticated, ]

    @swagger_auto_schema(tags=['Statistics'], manual_parameters=[
        openapi.Parameter('product_id', openapi.IN_QUERY, description="Filter by product ID", type=openapi.TYPE_INTEGER),
    ])
    def get(self, request):
        product_id = request.query_params.get('product_id')

        # Get all ProductInput and ProductOutput, optionally filtered by product_id
        product_inputs = ProductInput.objects.all()
        product_outputs = ProductOutput.objects.all()

        if product_id:
            product_inputs = product_inputs.filter(product_id=product_id)
            product_outputs = product_outputs.filter(product_id=product_id)

        # Annotate each queryset with a 'type' field to distinguish them
        product_inputs = product_inputs.annotate(type=F('input_quantity'))
        product_outputs = product_outputs.annotate(type=F('output_quantity'))

        # Combine and order the querysets by created_at
        combined_queryset = list(product_inputs) + list(product_outputs)
        combined_queryset.sort(key=lambda x: x.created_at)

        # Serialize the combined queryset
        serializer = CombinedProductSerializer(combined_queryset, many=True)
        return Response(serializer.data)



#### REPORT ####
class ReportAPIView(APIView):
    serializer_class = ReportSerializer
    authentication_classes = [JWTAuthentication]

    @swagger_auto_schema(
        tags=['Statistics'],
        manual_parameters=[
            openapi.Parameter('date', openapi.IN_QUERY, description="Date in format 'YYYY-MM-DD'", type=openapi.TYPE_STRING),
            openapi.Parameter('start_date', openapi.IN_QUERY, description="Start date in format 'YYYY-MM-DD'", type=openapi.TYPE_STRING),
            openapi.Parameter('end_date', openapi.IN_QUERY, description="End date in format 'YYYY-MM-DD'", type=openapi.TYPE_STRING),
            openapi.Parameter('category', openapi.IN_QUERY, description="Category ID", type=openapi.TYPE_INTEGER),
            openapi.Parameter('order_by', openapi.IN_QUERY, description="Order by field", type=openapi.TYPE_STRING, enum=['category', 'name', 'price', 'quantity']),
            openapi.Parameter('search', openapi.IN_QUERY, description="Search query", type=openapi.TYPE_STRING),
        ]
    )
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
            return Response({'error': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)

    def get_report_with_token(self, request):
        date_str = request.query_params.get('date')
        start_date_str = request.query_params.get('start_date')
        end_date_str = request.query_params.get('end_date')
        category_id = request.query_params.get('category')
        order_by = request.query_params.get('order_by')
        search_query = request.query_params.get('search')

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
        return Response(report_data)

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
