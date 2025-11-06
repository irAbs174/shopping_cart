from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create a router for ViewSets (if you want to use them later)
router = DefaultRouter()
# router.register('products', views.ProductViewSet)
# router.register('pricing-rules', views.PricingRuleViewSet)

urlpatterns = [
    # API endpoints
    path('products/', views.ProductListView.as_view(), name='product-list'),
    path('products/<int:pk>/', views.ProductDetailView.as_view(), name='product-detail'),
    path('pricing-rules/', views.PricingRuleListView.as_view(), name='pricing-rule-list'),
    path('pricing-rules/<int:pk>/', views.PricingRuleDetailView.as_view(), name='pricing-rule-detail'),
    path('calculate-cart/', views.CalculateCartView.as_view(), name='calculate-cart'),
    path('cart/', views.CartView.as_view(), name='cart-management'),
    path('cart/items/', views.CartItemView.as_view(), name='cart-items'),
    path('cart/items/<int:pk>/', views.CartItemDetailView.as_view(), name='cart-item-detail'),
    
    # Health check endpoint
    path('health/', views.HealthCheckView.as_view(), name='health-check'),
    
    # Include router URLs (for future ViewSet expansion)
    # path('', include(router.urls)),
]

# Alternative with router (more organized for larger APIs)
# urlpatterns = router.urls + [
#     path('calculate-cart/', views.CalculateCartView.as_view(), name='calculate-cart'),
#     path('health/', views.HealthCheckView.as_view(), name='health-check'),
# ]