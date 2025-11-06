from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Product, PricingRule
from .serializers import (
    ProductSerializer, 
    PricingRuleSerializer,
    CartItemInputSerializer,
    CartCalculationSerializer
)
from .services import PricingService

class ProductListView(APIView):
    def get(self, request):
        products = Product.objects.all()
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)

class PricingRuleListView(APIView):
    def get(self, request):
        rules = PricingRule.objects.filter(is_active=True)
        serializer = PricingRuleSerializer(rules, many=True)
        return Response(serializer.data)

class CalculateCartView(APIView):
    def post(self, request):
        input_serializer = CartItemInputSerializer(data=request.data, many=True)
        
        if input_serializer.is_valid():
            cart_data = input_serializer.validated_data
            result = PricingService.calculate_cart_total(cart_data)
            
            output_serializer = CartCalculationSerializer(data=result)
            if output_serializer.is_valid():
                return Response(output_serializer.validated_data)
            else:
                return Response(
                    output_serializer.errors, 
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        
        return Response(input_serializer.errors, status=status.HTTP_400_BAD_REQUEST)