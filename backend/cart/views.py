from rest_framework import status, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Product, PricingRule, Cart, CartItem
from .serializers import (
    ProductSerializer, 
    PricingRuleSerializer,
    CartItemInputSerializer,
    CartCalculationSerializer,
    CartSerializer,
    CartItemSerializer
)
from .services import PricingService

class HealthCheckView(APIView):
    """Health check endpoint for monitoring"""
    def get(self, request):
        return Response({
            "status": "healthy",
            "service": "shopping-cart-api",
            "version": "1.0.0"
        })

class ProductListView(generics.ListAPIView):
    """List all products"""
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

class ProductDetailView(generics.RetrieveAPIView):
    """Retrieve a specific product"""
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

class PricingRuleListView(generics.ListAPIView):
    """List all active pricing rules"""
    queryset = PricingRule.objects.filter(is_active=True)
    serializer_class = PricingRuleSerializer

class PricingRuleDetailView(generics.RetrieveAPIView):
    """Retrieve a specific pricing rule"""
    queryset = PricingRule.objects.all()
    serializer_class = PricingRuleSerializer

class CalculateCartView(APIView):
    """Calculate cart total with pricing rules applied"""
    
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

class CartView(APIView):
    """Cart management - create and retrieve carts"""
    
    def get(self, request, cart_id=None):
        """Get or create a cart"""
        if cart_id:
            cart = get_object_or_404(Cart, id=cart_id)
        else:
            # Create a new cart or get existing from session
            session_key = request.session.session_key
            if session_key:
                cart, created = Cart.objects.get_or_create(session_key=session_key)
            else:
                request.session.create()
                cart = Cart.objects.create(session_key=request.session.session_key)
        
        serializer = CartSerializer(cart)
        return Response(serializer.data)
    
    def post(self, request):
        """Create a new cart"""
        cart = Cart.objects.create()
        serializer = CartSerializer(cart)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class CartItemView(APIView):
    """Manage cart items"""
    
    def get(self, request):
        """Get cart items for a specific cart"""
        cart_id = request.query_params.get('cart_id')
        if not cart_id:
            return Response(
                {"error": "cart_id parameter is required"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        cart = get_object_or_404(Cart, id=cart_id)
        items = cart.items.all()
        serializer = CartItemSerializer(items, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        """Add item to cart"""
        serializer = CartItemSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CartItemDetailView(APIView):
    """Manage specific cart item"""
    
    def get(self, request, pk):
        """Get specific cart item"""
        item = get_object_or_404(CartItem, pk=pk)
        serializer = CartItemSerializer(item)
        return Response(serializer.data)
    
    def put(self, request, pk):
        """Update cart item quantity"""
        item = get_object_or_404(CartItem, pk=pk)
        serializer = CartItemSerializer(item, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk):
        """Remove item from cart"""
        item = get_object_or_404(CartItem, pk=pk)
        item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# ViewSet alternative for more complex APIs
# class ProductViewSet(viewsets.ModelViewSet):
#     queryset = Product.objects.all()
#     serializer_class = ProductSerializer