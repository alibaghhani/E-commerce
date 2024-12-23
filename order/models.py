from django.contrib.auth import get_user_model

from core.models import TimeStampMixin
from django.db import models

from products.models import Product

User = get_user_model()

class Order(TimeStampMixin):
    """
    order model
    """
    user = models.ForeignKey(to=User, on_delete=models.CASCADE, related_name='user_order')
    product_list = models.JSONField(default=dict)
    address = models.TextField(default='iran')
    total_price = models.FloatField(default='4.20')
    expired_at = None

    def __str__(self):
        return f"{self.user} --- {self.address}"






class DiscountCode(TimeStampMixin, models.Model):
    """
    discount coupon model

    -----fields-----
        code = models.CharField(max_length=8, blank=True, null=True, unique=True)

    """
    DISCOUNT_CHOICES = (
        ('percentage', '%'),
        ('cash', '$')
    )
    type_of_discount = models.CharField(choices=DISCOUNT_CHOICES, max_length=250, null=True, blank=True)
    discount = models.PositiveIntegerField(blank=True, null=True)
    code = models.CharField(max_length=8, blank=True, null=True, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='user_discount_code')

    def __str__(self):
        return "%s" % self.code
