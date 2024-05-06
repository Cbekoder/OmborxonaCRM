from rest_framework import generics, status
from rest_framework.response import Response
from product.models import Product, ProductInput, ProductOutput
from .serializers import ReportSerializer
from django.db.models import Sum
from datetime import datetime
from django.utils.timezone import make_aware

class ReportAPIView(generics.RetrieveAPIView):
    serializer_class = ReportSerializer
    queryset = None

    def get_queryset(self):
        return None

    def get(self, request, *args, **kwargs):
        start_date_str = request.GET.get('start_date')
        end_date_str = request.GET.get('end_date')

        try:
            start_date = make_aware(datetime.strptime(start_date_str, '%Y-%m-%d'))
            end_date = make_aware(datetime.strptime(end_date_str, '%Y-%m-%d'))
        except ValueError:
            return Response({'error': 'Invalid date format'}, status=status.HTTP_400_BAD_REQUEST)

        products = Product.objects.all()
        report_data = []

        for product in products:
            goods_in = ProductInput.objects.filter(product=product, created_at__range=(start_date, end_date)).aggregate(
                goods_in_quantity=Sum('input_quantity'),
                goods_in_price=Sum('input_quantity') * product.price
            )

            goods_out = ProductOutput.objects.filter(product=product, created_at__range=(start_date, end_date)).aggregate(
                goods_out_quantity=Sum('output_quantity'),
                goods_out_price=Sum('output_quantity') * product.price
            )

            # Calculate beginning quantity and price
            beginning_quantity = product.quantity or 0  # Default to 0 if quantity is None
            beginning_price = product.quantity * product.price if product.quantity else 0  # Default to 0 if quantity is None

            # Calculate last quantity and price
            last_quantity = beginning_quantity + (goods_in['goods_in_quantity'] or 0) - (goods_out['goods_out_quantity'] or 0)
            last_price = beginning_price + (goods_in['goods_in_price'] or 0) - (goods_out['goods_out_price'] or 0)

            # Check if all values are zero, if so, skip this product
            if all(value == 0 for value in [
                beginning_quantity,
                beginning_price,
                goods_in['goods_in_quantity'] or 0,
                goods_in['goods_in_price'] or 0,
                goods_out['goods_out_quantity'] or 0,
                goods_out['goods_out_price'] or 0,
                last_quantity,
                last_price
            ]):
                continue

            product_report = {
                'product_name': product.name,
                'product_code': product.prod_code,
                'product_unit': product.unit.name,
                'beginning_quantity': beginning_quantity,
                'beginning_price': beginning_price,
                'goods_in_quantity': goods_in['goods_in_quantity'] or 0,
                'goods_in_price': goods_in['goods_in_price'] or 0,
                'goods_out_quantity': goods_out['goods_out_quantity'] or 0,
                'goods_out_price': goods_out['goods_out_price'] or 0,
                'last_quantity': last_quantity,
                'last_price': last_price,
            }

            report_data.append(product_report)

        serializer = self.serializer_class(report_data, many=True)
        return Response(serializer.data)
