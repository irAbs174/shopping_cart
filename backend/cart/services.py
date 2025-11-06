from decimal import Decimal
from typing import List, Dict, Any
from django.db import transaction
from .models import Product, PricingRule

class PricingService:
    """
    سرویس محاسبه قیمت با اعمال قوانین قیمت‌گذاری
    طراحی شده برای افزودن قوانین جدید بدون نیاز به تغییر کد
    """
    
    @staticmethod
    def calculate_cart_total(cart_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        محاسبه قیمت نهایی سبد خرید با اعمال قوانین
        
        Args:
            cart_data: لیستی از دیکشنری‌های حاوی product_id و quantity
            
        Returns:
            دیکشنری حاوی جزئیات محاسبه قیمت
        """
        # محاسبه قیمت پایه
        base_total = Decimal('0')
        items_detail = []
        
        for item in cart_data:
            try:
                product = Product.objects.get(id=item['product_id'])
                quantity = item['quantity']
                item_total = product.price * quantity
                
                base_total += item_total
                items_detail.append({
                    'product_id': product.id,
                    'product_name': product.name,
                    'quantity': quantity,
                    'unit_price': float(product.price),
                    'total_price': float(item_total)
                })
            except Product.DoesNotExist:
                continue
        
        # اعمال قوانین قیمت‌گذاری
        rules = PricingRule.objects.filter(is_active=True).order_by('-priority', 'id')
        applied_rules = []
        final_total = base_total
        
        for rule in rules:
            discount_amount = PricingService._apply_rule(rule, items_detail, final_total)
            
            if discount_amount > 0:
                final_total -= discount_amount
                applied_rules.append({
                    'rule_name': rule.name,
                    'rule_type': rule.rule_type,
                    'discount_amount': float(discount_amount)
                })
        
        return {
            'base_total': float(base_total),
            'final_total': float(final_total),
            'total_discount': float(base_total - final_total),
            'items': items_detail,
            'applied_rules': applied_rules
        }
    
    @staticmethod
    def _apply_rule(rule: PricingRule, items_detail: List[Dict], current_total: Decimal) -> Decimal:
        """
        اعمال یک قانون قیمت‌گذاری خاص
        
        Args:
            rule: قانون قیمت‌گذاری
            items_detail: جزئیات آیتم‌های سبد خرید
            current_total: قیمت فعلی سبد خرید
            
        Returns:
            مقدار تخفیف اعمال شده
        """
        # بررسی شرط قانون
        if not PricingService._check_condition(rule, items_detail, current_total):
            return Decimal('0')
        
        # اعمال تخفیف بر اساس نوع قانون
        rule_methods = {
            'percentage_discount': PricingService._apply_percentage_discount,
            'fixed_discount': PricingService._apply_fixed_discount,
            'buy_x_get_y': PricingService._apply_buy_x_get_y,
            'bundle_discount': PricingService._apply_bundle_discount,
        }
        
        method = rule_methods.get(rule.rule_type)
        if method:
            return method(rule, items_detail, current_total)
        
        return Decimal('0')
    
    @staticmethod
    def _check_condition(rule: PricingRule, items_detail: List[Dict], current_total: Decimal) -> bool:
        """بررسی شرط قانون"""
        condition_type = rule.condition_type
        condition_value = rule.condition_value
        
        if condition_type == 'min_total':
            min_amount = Decimal(str(condition_value.get('min_amount', 0)))
            return current_total >= min_amount
        
        elif condition_type == 'min_quantity':
            min_qty = condition_value.get('min_quantity', 0)
            total_quantity = sum(item['quantity'] for item in items_detail)
            return total_quantity >= min_qty
        
        elif condition_type == 'product_based':
            product_id = condition_value.get('product_id')
            min_qty = condition_value.get('min_quantity', 1)
            
            for item in items_detail:
                if item['product_id'] == product_id and item['quantity'] >= min_qty:
                    return True
            return False
        
        return False
    
    @staticmethod
    def _apply_percentage_discount(rule: PricingRule, items_detail: List[Dict], current_total: Decimal) -> Decimal:
        """اعمال تخفیف درصدی"""
        discount_percentage = Decimal(str(rule.discount_value.get('percentage', 0)))
        return current_total * (discount_percentage / 100)
    
    @staticmethod
    def _apply_fixed_discount(rule: PricingRule, items_detail: List[Dict], current_total: Decimal) -> Decimal:
        """اعمال تخفیف ثابت"""
        discount_amount = Decimal(str(rule.discount_value.get('amount', 0)))
        return min(discount_amount, current_total)
    
    @staticmethod
    def _apply_buy_x_get_y(rule: PricingRule, items_detail: List[Dict], current_total: Decimal) -> Decimal:
        """اعمال قانون خرید X بگیر Y رایگان"""
        product_id = rule.condition_value.get('product_id')
        buy_x = rule.condition_value.get('buy_quantity', 1)
        get_y = rule.condition_value.get('get_free_quantity', 1)
        
        for item in items_detail:
            if item['product_id'] == product_id:
                product = Product.objects.get(id=product_id)
                free_units = (item['quantity'] // buy_x) * get_y
                return free_units * product.price
        
        return Decimal('0')
    
    @staticmethod
    def _apply_bundle_discount(rule: PricingRule, items_detail: List[Dict], current_total: Decimal) -> Decimal:
        """اعمال تخفیف باندل"""
        bundle_products = rule.condition_value.get('products', [])
        discount_type = rule.discount_value.get('type', 'percentage')
        discount_value = Decimal(str(rule.discount_value.get('value', 0)))
        
        # بررسی وجود تمام محصولات باندل در سبد خرید
        bundle_in_cart = True
        bundle_items = []
        
        for product_id in bundle_products:
            found = False
            for item in items_detail:
                if item['product_id'] == product_id and item['quantity'] >= 1:
                    bundle_items.append(item)
                    found = True
                    break
            if not found:
                bundle_in_cart = False
                break
        
        if not bundle_in_cart or not bundle_items:
            return Decimal('0')
        
        # محاسبه تخفیف
        if discount_type == 'percentage':
            bundle_total = sum(Decimal(str(item['total_price'])) for item in bundle_items)
            return bundle_total * (discount_value / 100)
        elif discount_type == 'fixed':
            return discount_value
        
        return Decimal('0')