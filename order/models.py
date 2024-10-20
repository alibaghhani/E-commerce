from django.contrib.postgres.fields import ArrayField
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

import products
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

    def get_prices(self):
        products = [item['id'] for item in self.products_list]
        prices = []
        for id in products:
            prices.append(Product.objects.get(id=id).price)
        return prices

    @property
    def sum_of_prices(self):
        return sum(self.get_prices())

    @property
    def receipt(self):
        return {}
