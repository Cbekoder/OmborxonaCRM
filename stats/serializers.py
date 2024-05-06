from rest_framework import serializers

class ReportSerializer(serializers.Serializer):
    product_name = serializers.CharField()
    product_code = serializers.CharField()
    product_unit = serializers.CharField()
    beginning_quantity = serializers.IntegerField()
    beginning_price = serializers.IntegerField()
    goods_in_quantity = serializers.IntegerField()
    goods_in_price = serializers.IntegerField()
    goods_out_quantity = serializers.IntegerField()
    goods_out_price = serializers.IntegerField()
    last_quantity = serializers.IntegerField()
    last_price = serializers.IntegerField()
