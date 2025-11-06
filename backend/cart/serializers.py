from rest_framework import serializers
from .models import Product, PricingRule, Cart, CartItem

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'

class PricingRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = PricingRule
        fields = '__all__'

class CartItemInputSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1)

class CartCalculationSerializer(serializers.Serializer):
    base_total = serializers.FloatField()
    final_total = serializers.FloatField()
    total_discount = serializers.FloatField()
    items = serializers.JSONField()
    applied_rules = serializers.JSONField()