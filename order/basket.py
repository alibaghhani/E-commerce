from django.http import HttpRequest
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import ValidationError
import json
from config.settings import redis_client
from products.models import Product


class BasketRedisAdapter:
    __client = redis_client

    def __init__(self, request: HttpRequest = None, product=None, quantity=None, address=None):
        self.request = request
        self.product = product
        self.quantity = quantity
        self.address = address
        self.user = self.request.user.id
        self.basket_to_display = {}

    def check_if_basket_exists(self):
        return self.__class__.__client.exists(f"user:{self.user}") == 1

    def add_to_basket(self):
        if not self.product or self.quantity is None:
            raise ValueError("product and quantity must be specified.")
        if self.check_warehouse(self.product, self.quantity):
            if not self.__class__.__client.hexists(f"user:{self.user}", self.product):

                self.__class__.__client.hset(f"user:{self.user}", self.product, self.quantity)
                self.change_stock()

            else:
                raise ValueError('product already exists in basket')
        return True

    def delete_from_basket(self):
        if not self.__class__.__client.hexists(f"user:{self.user}", self.product):
            raise ValueError("Product not found in basket.")

        self.__class__.__client.hdel(f"user:{self.user}", self.product)
        self.change_stock()
        return True

    def display_basket(self):
        basket = self.__class__.__client.hgetall(f"user:{self.user}")
        basket_dict = {key.decode('utf-8'): value.decode('utf-8') for key, value in basket.items()}
        address = None
        for key, value in basket_dict.items():
            if key == "address":
                address = value
                continue

            if key.isdigit():
                try:
                    product = Product.objects.get(id=str(key))
                    self.basket_to_display[product.name] = value
                except Product.DoesNotExist:
                    continue

        if address:
            self.basket_to_display["address"] = address
        self.basket_to_display['total_price'] = self.total_price
        return self.basket_to_display

    def add_or_update_address(self):
        print(self.address)
        if self.request.method == "POST":
            if not self.address:
                raise ValueError("address must be set!")

            value = self.__class__.__client.hget(f"user:{self.user}", "address").decode('utf-8')
            if str(self.address) == str(value):
                raise ValueError("address already exists!")


        self.__class__.__client.hset(f"user:{self.user}", "address", self.address)


    def update_basket(self):
        if not self.product or self.quantity is None:
            raise ValueError("product and quantity must be specified.")
        if self.check_warehouse(self.product, self.quantity):
            self.__class__.__client.hset(f"user:{self.user}", self.product, self.quantity)
            self.change_stock()


    @staticmethod
    def check_warehouse(product_id, quantity):
        available_in_stock = Product.objects.get(id=product_id).warehouse
        if int(quantity) > available_in_stock:
            raise ValueError("product not available in stock!")
        return True


    def get_total_price(self):
        basket = self.__class__.__client.hgetall(f"user:{self.user}")
        basket_dict = {key.decode('utf-8'): value.decode('utf-8') for key, value in basket.items()}
        if 'address' in basket_dict:
            del basket_dict['address']
        list_of_prices = []
        for key, value in basket_dict.items():
            price = Product.objects.get(id=str(key)).price
            list_of_prices.append(price*int(value))

        return list_of_prices

    @property
    def total_price(self):
        return sum(self.get_total_price())


    def change_stock(self):
        product_stock = Product.objects.get(id=self.product).warehouse
        if self.request.method in ["POST", "PATCH"]:
            Product.objects.filter(id=self.product).update(warehouse=product_stock-int(self.quantity))

            return True
        Product.objects.filter(id=self.product).update(warehouse=product_stock+int(self.quantity))
        return True



