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
            first_good_in = ProductInput.objects.filter(product=product, created_at__range=(start_date, end_date)).order_by("created_at").first()
            last_good_in = ProductInput.objects.filter(product=product, created_at__range=(start_date, end_date)).order_by("created_at").last()

            goods_out = ProductOutput.objects.filter(product=product, created_at__range=(start_date, end_date)).aggregate(
                goods_out_quantity=Sum('output_quantity'),
                goods_out_price=Sum('output_quantity') * product.price
            )
            first_good_out = ProductOutput.objects.filter(product=product, created_at__range=(start_date, end_date)).order_by('created_at').first()
            last_good_out = ProductOutput.objects.filter(product=product, created_at__range=(start_date, end_date)).order_by('created_at').last()

            if first_good_in and first_good_out:
                if first_good_in.created_at < first_good_out.created_at:
                    beginning_quantity = first_good_in.all_quantity - first_good_in.input_quantity
                else:
                    beginning_quantity = first_good_out.all_quantity + first_good_out.output_quantity
            elif first_good_in:
                beginning_quantity = first_good_in.all_quantity - first_good_in.input_quantity
            elif first_good_out:
                beginning_quantity = first_good_out.all_quantity + first_good_out.output_quantity
            else:
                beginning_quantity = 0  
            beginning_price = beginning_quantity * product.price if beginning_quantity else 0

            if last_good_in and last_good_out:
                if last_good_in.created_at > last_good_out.created_at:
                    last_quantity = last_good_in.all_quantity
                else:
                    last_quantity = last_good_out.all_quantity
            elif last_good_in:
                last_quantity = last_good_in.all_quantity
            elif last_good_out:
                last_quantity = last_good_out.all_quantity
            else:
                last_quantity = 0  
            last_price = last_quantity * product.price if last_quantity else 0

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
