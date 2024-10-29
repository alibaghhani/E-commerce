import uuid
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.http import HttpRequest

from authentication.models import User, Address
from config.settings import redis_client_first_db, redis_client_second_db
from order.models import DiscountCode, Order
from products.models import Product, Discount


class BasketAndOrderRedisAdapter:
    __client = redis_client_first_db
    __payment_client = redis_client_second_db

    __address = Address()
    __order = Order()

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
                self.__class__.__client.hset(f"user:{self.user}", "pay_amount", self.total_price)
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
                    self.basket_to_display['product_uuid'] = product.slug
                except Product.DoesNotExist:
                    continue

        if address:
            self.basket_to_display["address"] = address
        if self.__class__.__client.hexists(f"user:{self.user}", "pay_amount"):
            price_after_discount = self.__class__.__client.hget(f"user:{self.user}", "pay_amount")
            self.basket_to_display['total_price'] = float(self.total_price)
            self.basket_to_display['price_after_discount'] = float(price_after_discount)
        else:
            self.basket_to_display['total_price'] = self.total_price


        return self.basket_to_display

    def add_or_update_address(self):
        if self.request.method == "POST":
            if not self.address:
                raise ValueError("address must be set!")

            value = self.__class__.__client.hget(f"user:{self.user}", "address")
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
            if key.isdigit():
                try:
                    price = Product.objects.get(id=str(key)).price
                    list_of_prices.append(price * int(value))
                except Product.DoesNotExist:
                    continue

        return list_of_prices

    @property
    def total_price(self):
        return sum(self.get_total_price())

    def change_stock(self):
        product_stock = Product.objects.get(id=self.product).warehouse
        if self.request.method in ["POST", "PATCH"]:
            Product.objects.filter(id=self.product).update(warehouse=product_stock - int(self.quantity))

            return True
        Product.objects.filter(id=self.product).update(warehouse=product_stock + int(self.quantity))
        return True

    def set_payment_information(self, message=None):
        user = get_user_model().objects.get(id=self.user).uuid
        pay_amount = self.__class__.__client.hget(f"user:{self.user}", "pay_amount")
        self.__class__.__payment_client.hset(
            f"payment:{str(user)}",
            mapping={
                "total_price": pay_amount,
                "user": str(user),
                "payment_id": str(uuid.uuid4()),
                "status": str(message)
            }
        )
        return self.__class__.__payment_client.hgetall(f"payment:{user}")

    @property
    def payment_information(self):
        return self.set_payment_information()

    def check_discount(self, code):
        user = User.objects.get(id=self.user)
        if user.user_discount_code.filter(code=code).exists():
            discount_type = DiscountCode.objects.get(code=code).type_of_discount
            discount = DiscountCode.objects.get(code=code).discount
            return [discount_type, discount]
        return None

    @staticmethod
    def calculate_discount(discount_information: list, total_price):
        assert len(discount_information) == 2, "invalid input"
        if discount_information[0] == 'cash':
            discounted_price = total_price - int(discount_information[1])
            return discounted_price
        discounted_price = total_price - (total_price * (int(discount_information[1]) / 100))
        return discounted_price

    def apply_discount(self, code):
        total_price = int(self.total_price)
        discount_information = self.check_discount(code=code)

        if discount_information:
            amount_to_pay = self.calculate_discount(discount_information=discount_information, total_price=total_price)

            stored_discount = self.__class__.__client.hget(f"user:{self.user}", "discount")

            if stored_discount is not None and stored_discount.decode('utf-8') == '1':
                raise ValueError('You have already used this code')

            self.__class__.__client.hset(f"user:{self.user}", mapping={
                "pay_amount": amount_to_pay,
                "discount": 1
            })
            return True
        else:
            # self.__class__.__client.hset(f"user:{self.user}", "pay_amount", self.total_price)
            raise RuntimeError('Invalid code!')

    def flush_basket(self):
        try:
            self.__class__.__client.delete(f"user:{self.user}")
            return True
        except Exception:
            return False

    def create_order(self):
        basket_copy = self.display_basket().copy()
        user = get_user_model().objects.get(id=self.user)
        order = Order.objects.create(user=user)

        if 'address' in basket_copy:
            order.address = self.get_address(int(basket_copy['address']))
            order.save()
            del basket_copy['address']

        if 'price_after_discount' not in basket_copy:
            raise ValueError("basket is not completed yet")

        order.total_price = basket_copy['price_after_discount']
        order.save()
        del basket_copy['price_after_discount']

        order.product_list = basket_copy
        order.save()

        self.flush_basket()
        return True

    def get_address(self, id):
        address = Address.objects.get(id=id)
        return address.full_address

    def validate_basket(self):
        if self.__class__.__client.hexists(f"user:{self.user}", "address") and self.__class__.__client.hexists(
                f"user:{self.user}", "pay_amount"):
            return True
        raise ValidationError("basket is not complete!")
