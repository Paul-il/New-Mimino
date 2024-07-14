from rest_framework import serializers

class OrderSummarySerializer(serializers.Serializer):
    total_orders_today = serializers.IntegerField()
    total_orders_sum = serializers.DecimalField(max_digits=10, decimal_places=2)
    total_pickup_orders_today = serializers.IntegerField()
    total_pickup_orders_sum = serializers.DecimalField(max_digits=10, decimal_places=2)
    total_delivery_orders_today = serializers.IntegerField()
    total_delivery_orders_sum = serializers.DecimalField(max_digits=10, decimal_places=2)
    total_all_orders_today = serializers.IntegerField()
    total_all_orders_sum = serializers.DecimalField(max_digits=10, decimal_places=2)

class TipSummarySerializer(serializers.Serializer):
    order_id = serializers.IntegerField()
    order_amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    tip_amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    created_by = serializers.CharField()
    users = serializers.ListField(
        child=serializers.DictField()
    )

class ProductSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    product_name_rus = serializers.CharField(max_length=255)
    is_available = serializers.BooleanField()
