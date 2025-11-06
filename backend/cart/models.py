from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal

class Product(models.Model):
    name = models.CharField(max_length=200)
    price = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class PricingRule(models.Model):
    RULE_TYPES = [
        ('percentage_discount', 'Percentage Discount'),
        ('fixed_discount', 'Fixed Discount'),
        ('buy_x_get_y', 'Buy X Get Y Free'),
        ('bundle_discount', 'Bundle Discount'),
    ]
    
    CONDITION_TYPES = [
        ('min_total', 'Minimum Total Amount'),
        ('min_quantity', 'Minimum Quantity'),
        ('product_based', 'Product Based'),
    ]
    
    name = models.CharField(max_length=200)
    rule_type = models.CharField(max_length=50, choices=RULE_TYPES)
    condition_type = models.CharField(max_length=50, choices=CONDITION_TYPES)
    condition_value = models.JSONField(help_text="Condition parameters in JSON format")
    discount_value = models.JSONField(help_text="Discount parameters in JSON format")
    is_active = models.BooleanField(default=True)
    priority = models.IntegerField(default=0, help_text="Higher priority rules apply first")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-priority', 'id']

    def __str__(self):
        return f"{self.name} ({self.rule_type})"

class Cart(models.Model):
    session_key = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cart {self.id}"

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['cart', 'product']

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"