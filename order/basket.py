from django.http import HttpRequest
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import ValidationError
import json
from config.settings import redis_client
from products.models import Product


class BasketRedisAdapter:
    __client = redis_client

    def __init__(self, request: HttpRequest = None, product=None, quantity=None):
        self.request = request
        self.product = product
        self.quantity = quantity
        self.user = self.request.user.id

    def check_if_basket_exists(self):
        return self.__class__.__client.exists(f"user:{self.user}") == 1

    def add_to_basket(self):
        if not self.product or self.quantity is None:
            raise ValueError("product and quantity must be specified.")

        self.__class__.__client.hset(f"user:{self.user}", self.product, self.quantity)
        return True

    def delete_from_basket(self):
        if not self.__class__.__client.hexists(f"user:{self.user}", self.product):
            raise ValueError("Product not found in basket.")

        self.__class__.__client.hdel(f"user:{self.user}", self.product)
        return True

    def display_basket(self):
        basket_to_display = {}
        basket = self.__class__.__client.hgetall(f"user:{self.user}")
        basket_dict = {key.decode('utf-8'): value.decode('utf-8') for key, value in basket.items()}
        for key, value in basket_dict.items():
            product = Product.objects.get(id=str(key))
            basket_to_display[product.name] = value
        return basket_to_display







