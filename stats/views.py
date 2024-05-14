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
        date_str = request.GET.get('date')
        start_date_str = request.GET.get('start_date')
        end_date_str = request.GET.get('end_date')

        if date_str and (start_date_str or end_date_str):
            return Response({'error': 'Cannot use both date and start_date/end_date parameters simultaneously'},
                            status=status.HTTP_400_BAD_REQUEST)
        if date_str:
            try:
                date = make_aware(datetime.strptime(date_str, '%Y-%m-%d'))
            except ValueError:
                return Response({'error': 'Invalid date format'}, status=status.HTTP_400_BAD_REQUEST)

            products = Product.objects.all()
            report_data = self.generate_report_data(products, date=date)

        elif start_date_str and end_date_str:
            try:
                start_date = make_aware(datetime.strptime(start_date_str, '%Y-%m-%d'))
                end_date = make_aware(datetime.strptime(end_date_str, '%Y-%m-%d'))
            except ValueError:
                return Response({'error': 'Invalid date format'}, status=status.HTTP_400_BAD_REQUEST)

            products = Product.objects.all()
            report_data = self.generate_report_data(products, start_date=start_date, end_date=end_date)

        else:
            products = Product.objects.all()
            report_data = self.generate_report_data(products)

        serializer = self.serializer_class(report_data, many=True)
        return Response(serializer.data)

    def generate_report_data(self, products, date=None, start_date=None, end_date=None):
        report_data = []

        for product in products:
            goods_in = ProductInput.objects.filter(product=product)
            goods_out = ProductOutput.objects.filter(product=product)

            if date:
                goods_in = goods_in.filter(created_at__date=date)
                goods_out = goods_out.filter(created_at__date=date)
            elif start_date and end_date:
                goods_in = goods_in.filter(created_at__range=(start_date, end_date))
                goods_out = goods_out.filter(created_at__range=(start_date, end_date))

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

