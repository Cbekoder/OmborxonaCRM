from django.shortcuts import get_object_or_404
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from django.http import JsonResponse
from django.utils.timezone import make_aware
from datetime import datetime, time
from django.db.models import Sum, F
from rest_framework.views import APIView
from rest_framework import status
from django.db.models import Q
from rest_framework_simplejwt.authentication import JWTAuthentication

from product.models import Product, ProductInput, ProductOutput
from product.serializers import ProductInputGetSerializer, ProductOutputGetSerializer, CombinedProductSerializer, \
    ProductReportSerializer
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
        openapi.Parameter('product_id', openapi.IN_QUERY, description="Filter by product ID",
                          type=openapi.TYPE_INTEGER),
        openapi.Parameter('start_date', openapi.IN_QUERY, description="Start date in format 'YYYY-MM-DD'",
                          type=openapi.TYPE_STRING),
        openapi.Parameter('end_date', openapi.IN_QUERY, description="End date in format 'YYYY-MM-DD'",
                          type=openapi.TYPE_STRING),
        openapi.Parameter('category', openapi.IN_QUERY, description="Category ID", type=openapi.TYPE_INTEGER),
        openapi.Parameter('order_by', openapi.IN_QUERY, description="Order by field", type=openapi.TYPE_STRING,
                          enum=['category', 'name', 'price', 'quantity']),
        openapi.Parameter('search', openapi.IN_QUERY, description="Search query", type=openapi.TYPE_STRING),
    ])
    def get(self, request):
        product_inputs = ProductInput.objects.all()

        start_date_str = request.query_params.get('start_date')
        end_date_str = request.query_params.get('end_date')
        category_id = request.query_params.get('category')
        order_by = request.query_params.get('order_by')
        search_query = request.query_params.get('search')

        # Filter by product_id if provided in query parameters
        product_id = request.query_params.get('product_id')
        if product_id:
            product_inputs = product_inputs.filter(product_id=product_id)

        if category_id:
            product_inputs = product_inputs.filter(category_id=category_id)

        if order_by:
            if order_by == 'category':
                product_inputs = product_inputs.order_by('category__name')
            elif order_by == 'name':
                product_inputs = product_inputs.order_by('name')
            elif order_by == 'price':
                product_inputs = product_inputs.order_by('price')
            elif order_by == 'quantity':
                product_inputs = product_inputs.order_by('quantity')

        serializer = ProductInputGetSerializer(product_inputs, many=True)
        return Response(serializer.data)


#### OUTPUTS ####

class ProductOutputsListAPIView(APIView):
    """
    List all product outputs or create a new one.
    """
    permission_classes = [IsAuthenticated, ]

    @swagger_auto_schema(tags=['Statistics'], manual_parameters=[
        openapi.Parameter('product_id', openapi.IN_QUERY, description="Filter by product ID",
                          type=openapi.TYPE_INTEGER),
        openapi.Parameter('start_date', openapi.IN_QUERY, description="Start date in format 'YYYY-MM-DD'",
                          type=openapi.TYPE_STRING),
        openapi.Parameter('end_date', openapi.IN_QUERY, description="End date in format 'YYYY-MM-DD'",
                          type=openapi.TYPE_STRING),
        openapi.Parameter('category', openapi.IN_QUERY, description="Category ID", type=openapi.TYPE_INTEGER),
        openapi.Parameter('order_by', openapi.IN_QUERY, description="Order by field", type=openapi.TYPE_STRING,
                          enum=['category', 'name', 'price', 'quantity']),
        openapi.Parameter('search', openapi.IN_QUERY, description="Search query", type=openapi.TYPE_STRING),
    ])
    def get(self, request):
        product_outputs = ProductOutput.objects.all()

        start_date_str = request.query_params.get('start_date')
        end_date_str = request.query_params.get('end_date')
        category_id = request.query_params.get('category')
        order_by = request.query_params.get('order_by')
        search_query = request.query_params.get('search')

        if category_id:
            product_outputs = product_outputs.filter(category_id=category_id)

        if order_by:
            if order_by == 'category':
                product_outputs = product_outputs.order_by('category__name')
            elif order_by == 'name':
                product_outputs = product_outputs.order_by('name')
            elif order_by == 'price':
                product_outputs = product_outputs.order_by('price')
            elif order_by == 'quantity':
                product_outputs = product_outputs.order_by('quantity')

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
        openapi.Parameter('product_id', openapi.IN_QUERY, description="Filter by product ID",
                          type=openapi.TYPE_INTEGER),
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
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.start_date = make_aware(datetime.strptime("2020-01-01", '%Y-%m-%d'))
        self.end_date = make_aware(
            datetime.combine(datetime.now().date(), time.max))

    @swagger_auto_schema(
        tags=['Statistics'],
        manual_parameters=[
            openapi.Parameter('start_date', openapi.IN_QUERY, description="Start date in format 'YYYY-MM-DD'",
                              type=openapi.TYPE_STRING),
            openapi.Parameter('end_date', openapi.IN_QUERY, description="End date in format 'YYYY-MM-DD'",
                              type=openapi.TYPE_STRING),
            openapi.Parameter('category', openapi.IN_QUERY, description="Category ID", type=openapi.TYPE_INTEGER),
            openapi.Parameter('order_by', openapi.IN_QUERY, description="Order by field", type=openapi.TYPE_STRING,
                              enum=['category', 'name', 'price', 'quantity']),
            openapi.Parameter('search', openapi.IN_QUERY, description="Search query", type=openapi.TYPE_STRING),
        ]
    )
    def get(self, request, *args, **kwargs):
        start_date_str = request.query_params.get('start_date')
        end_date_str = request.query_params.get('end_date')
        category_id = request.query_params.get('category')
        order_by = request.query_params.get('order_by')
        search_query = request.query_params.get('search')

        products = Product.objects.all()

        if category_id:
            products = products.filter(category_id=category_id)

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
        if start_date_str and end_date_str:
            if start_date_str > end_date_str:
                return Response({'error': 'Boshlanish sanasi yakuniy sanadan keyin bo\'lishi mumkin emas.'},
                                status=status.HTTP_400_BAD_REQUEST)
            try:
                self.start_date = make_aware(datetime.strptime(start_date_str, '%Y-%m-%d'))
                self.end_date = make_aware(
                    datetime.combine(datetime.strptime(end_date_str, '%Y-%m-%d').date(), time.max))
                products = products.filter(
                    productinput__created_at__range=(self.start_date, self.end_date),
                    productoutput__created_at__range=(self.start_date, self.end_date)
                ).distinct()
            except ValueError:
                return {'error': 'Invalid date format'}
        elif start_date_str or end_date_str:
            if start_date_str:
                if start_date_str > datetime.now().strftime('%Y-%m-%d'):
                    return Response({'error': 'Boshlanish sanasi bugungi sanadan keyin bo\'lishi mumkin emas.'},
                                    status=status.HTTP_400_BAD_REQUEST)
                try:
                    self.start_date = make_aware(datetime.strptime(start_date_str, '%Y-%m-%d'))
                    self.end_date = make_aware(datetime.now())

                except ValueError:
                    return {'error': 'Invalid date format'}
            else:
                try:
                    self.start_date = make_aware(datetime.strptime("2020-01-01", '%Y-%m-%d'))
                    self.end_date = make_aware(
                        datetime.combine(datetime.strptime(end_date_str, '%Y-%m-%d').date(), time.max))
                    products = products.filter(
                        productinput__created_at__range=(self.start_date, self.end_date),
                        productoutput__created_at__range=(self.start_date, self.end_date)
                    ).distinct()
                except ValueError:
                    return {'error': 'Invalid date format'}

        if search_query:
            products = products.filter(
                Q(prod_code__icontains=search_query) |
                Q(name__icontains=search_query) |
                Q(category__name__icontains=search_query)
            )
        report_data = []

        for product in products:
            goods_in = ProductInput.objects.filter(product=product, created_at__range=(self.start_date, self.end_date))
            goods_out = ProductOutput.objects.filter(product=product,
                                                     created_at__range=(self.start_date, self.end_date))

            goods_in_quantity = goods_in.aggregate(goods_in_quantity=Sum('input_quantity'))['goods_in_quantity'] or 0
            goods_in_price = goods_in_quantity * product.price

            goods_out_quantity = goods_out.aggregate(goods_out_quantity=Sum('output_quantity'))[
                                     'goods_out_quantity'] or 0
            goods_out_price = goods_out_quantity * product.price

            if goods_in.first() and goods_out.first():
                if goods_in.first().created_at <= goods_out.first().created_at:
                    beginning_quantity = goods_in.first().all_quantity - goods_in.first().input_quantity
                else:
                    beginning_quantity = goods_out.first().all_quantity + goods_out.first().output_quantity
            elif goods_in.first() or goods_out.first():
                if goods_in.first():
                    beginning_quantity = goods_in.first().all_quantity - goods_in.first().input_quantity

                else:
                    beginning_quantity = goods_out.first().all_quantity + goods_out.first().output_quantity
            else:
                beginning_quantity = 0
            beginning_price = beginning_quantity * product.price if beginning_quantity else 0

            if goods_in.last() and goods_out.last():
                if goods_in.last().created_at >= goods_out.last().created_at:
                    last_quantity = goods_in.last().all_quantity
                else:
                    last_quantity = goods_out.last().all_quantity
            elif goods_in.last() or goods_out.last():
                if goods_in.last():
                    last_quantity = goods_in.last().all_quantity
                else:
                    last_quantity = goods_out.last().all_quantity
            else:
                last_quantity = 0
            last_price = last_quantity * product.price if last_quantity else 0

            if all(value == 0 for value in [
                beginning_quantity, beginning_price, goods_in_quantity, goods_in_price,
                goods_out_quantity, goods_out_price, last_quantity, last_price
            ]):
                continue
            serializer = ProductReportSerializer(product)
            product_report = {
                'product': serializer.data,
                'beginning': {
                    "quantity": beginning_quantity,
                    'price': beginning_price
                },
                'input': {
                    'quantity': goods_in_quantity,
                    'price': goods_in_price,
                },
                'output': {
                    'quantity': goods_out_quantity,
                    'price': goods_out_price,
                },
                'last': {
                    'quantity': last_quantity,
                    'last_price': last_price
                }
            }
            report_data.append(product_report)
        return JsonResponse(report_data, safe=False)
