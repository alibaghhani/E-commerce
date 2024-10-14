from django.contrib.postgres.fields import ArrayField
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from authentication.models import CustomerProfile
from core.models import TimeStampMixin
from products.models import Product


class Basket(TimeStampMixin):
    expired_at = None
    updated_at = None
    products_list = ArrayField(models.JSONField(null=True, blank=True), null=True, blank=True)
    customer = models.OneToOneField(CustomerProfile, on_delete=models.CASCADE, related_name='customer_basket')

    def __str__(self):
        return f"{self.customer}"

    def display_products(self):
        products_to_display = {}
        products_to_display.update(_ for _ in self.products_list)


