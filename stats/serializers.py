from rest_framework import serializers

class ReportSerializer(serializers.Serializer):
    product_name = serializers.CharField()
    product_code = serializers.CharField()
    product_unit = serializers.CharField()
    first_quantity = serializers.IntegerField()
    first_price = serializers.IntegerField()
    in_quantity = serializers.IntegerField()
    in_price = serializers.IntegerField()
    out_quantity = serializers.IntegerField()
    out_price = serializers.IntegerField()
    last_quantity = serializers.IntegerField()
    last_price = serializers.IntegerField()
