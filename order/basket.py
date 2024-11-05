import json
import uuid
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.http import HttpRequest
from authentication.models import User, Address
from config.settings import redis_client_first_db, redis_client_second_db
from order.models import DiscountCode, Order
from products.models import Product, Discount


class BasketAndOrderRedisAdapter:
    """
    This class handles basket and order operations using Redis as a database.

    Attributes:
        request: HttpRequest object associated with the current request.
        product: ID of the product being manipulated in the basket.
        quantity: Quantity of the product to be added or updated in the basket.
        address: ID of the address associated with the order.
        user: ID of the user associated with the current request.
        basket_to_display: Dictionary to hold basket data for display.
    """
    __client = redis_client_first_db
    __payment_client = redis_client_second_db

    def __init__(self, request: HttpRequest = None, product=None, quantity=None, address=None):
        self.request = request
        self.product = product
        self.quantity = quantity
        self.address = address
        self.user = self.request.user.id
        self.basket_to_display = {}

    def check_if_basket_exists(self):
        """
        Check if the user's basket exists in Redis.

        Returns:
            bool: True if the basket exists, otherwise False.
        """
        return self.__class__.__client.exists(f"user:{self.user}") == 1

    def add_to_basket(self):
        """
        Adds a specified product and quantity to the basket.

        Raises:
            ValueError: If product or quantity not specified, or if the product is already in the basket.

        Returns:
            bool: True if the product is added successfully.
        """
        if not self.product or self.quantity is None:
            raise ValueError("Product and quantity must be specified.")

        if self.check_warehouse(self.product, self.quantity):
            if not self.__class__.__client.hexists(f"user:{self.user}", self.product):
                self.__class__.__client.hset(f"user:{self.user}", self.product, self.quantity)
                self.__class__.__client.hset(f"user:{self.user}", "pay_amount", self.total_price)
                self.change_stock()
            else:
                raise ValueError('Product already exists in basket')
        return True

    def delete_from_basket(self):
        """
        Deletes a specified product from the basket if it exists.

        Raises:
            ValueError: If the product is not found in the basket.

        Returns:
            bool: True if the product is deleted successfully.
        """
        if not self.__class__.__client.hexists(f"user:{self.user}", self.product):
            raise ValueError("Product not found in basket.")

        self.__class__.__client.hdel(f"user:{self.user}", self.product)
        self.change_stock()
        return True

    def display_basket(self):
        """
        Returns a JSON serializable view of the basket for display.

        Returns:
            dict: A dictionary representation of the user's basket.
        """
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
        if self.__class__.__client.hexists(f"user:{self.user}", "pay_amount"):
            price_after_discount = self.__class__.__client.hget(f"user:{self.user}", "pay_amount")
            self.basket_to_display['total_price'] = float(self.total_price)
            self.basket_to_display['price_after_discount'] = float(price_after_discount)
        else:
            self.basket_to_display['total_price'] = self.total_price

        return self.basket_to_display

    def add_or_update_address(self):
        """
        Adds or updates the address in the user's basket.

        Raises:
            ValueError: If the address is not provided or already exists.
        """
        if self.request.method == "POST":
            if not self.address:
                raise ValueError("Address must be set!")

            value = self.__class__.__client.hget(f"user:{self.user}", "address")
            if str(self.address) == str(value):
                raise ValueError("Address already exists!")

        self.__class__.__client.hset(f"user:{self.user}", "address", self.address)

    def update_basket(self):
        """
        Updates the quantity of a specified product in the basket.

        Raises:
            ValueError: If product or quantity not specified.
        """
        if not self.product or self.quantity is None:
            raise ValueError("Product and quantity must be specified.")

        if self.check_warehouse(self.product, self.quantity):
            self.__class__.__client.hset(f"user:{self.user}", self.product, self.quantity)
            self.change_stock()

    @staticmethod
    def check_warehouse(product_id, quantity):
        """
        Checks if the specified quantity of a product is available in stock.

        Args:
            product_id (int): The ID of the product being checked.
            quantity (int): The quantity requested.

        Raises:
            ValueError: If requested quantity exceeds available stock.

        Returns:
            bool: True if the requested quantity is available, otherwise raises ValueError.
        """
        available_in_stock = Product.objects.get(id=product_id).warehouse
        if int(quantity) > available_in_stock:
            raise ValueError("Product not available in stock!")
        return True

    def get_total_price(self):
        """
        Calculates the total price of items in the basket.

        Returns:
            list: A list of calculated prices for each product in the basket.
        """
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
        """
        Computes the total price of items in the basket.

        Returns:
            float: The total price calculated from all basket items.
        """
        return sum(self.get_total_price())

    def change_stock(self):
        """
        Updates the product stock based on remaining items after adding or removing from basket.

        Returns:
            bool: True if the stock is changed successfully.
        """
        product_stock = Product.objects.get(id=self.product).warehouse
        if self.request.method in ["POST", "PATCH"]:
            Product.objects.filter(id=self.product).update(warehouse=product_stock - int(self.quantity))
            return True
        Product.objects.filter(id=self.product).update(warehouse=product_stock + int(self.quantity))
        return True

    def set_payment_information(self, message=None):
        """
        Sets payment information in the payment Redis client for the user.

        Args:
            message (str): Custom message for payment status.

        Returns:
            dict: A dictionary of stored payment information.
        """
        user = get_user_model().objects.get(id=self.user).uuid
        if self.__class__.__client.hexists(f"user:{self.user}", "pay_amount"):
            pay_amount = self.__class__.__client.hget(f"user:{self.user}", "pay_amount")
        else:
            pay_amount = self.total_price
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
        """
        Gets payment information for the user.

        Returns:
            dict: Payment information stored in payment Redis client.
        """
        return self.set_payment_information()

    def check_discount(self, code):
        """
        Checks if the user is eligible for a discount using the provided discount code.

        Args:
            code (str): The discount code to be checked.

        Returns:
            list|None: A list containing discount type and value if valid, otherwise None.
        """
        user = User.objects.get(id=self.user)
        if user.user_discount_code.filter(code=code).exists():
            discount_type = DiscountCode.objects.get(code=code).type_of_discount
            discount = DiscountCode.objects.get(code=code).discount
            return [discount_type, discount]
        return None

    @staticmethod
    def calculate_discount(discount_information: list, total_price):
        """
        Applies the discount on the total price based on the discount information.

        Args:
            discount_information (list): A list with discount type and value.
            total_price (float): The original total price before discount.

        Returns:
            float: The new total price after applying the discount.

        Raises:
            AssertionError: If the discount_information list does not contain exactly 2 elements.
        """
        assert len(discount_information) == 2, "Invalid input"
        if discount_information[0] == 'cash':
            discounted_price = total_price - int(discount_information[1])
            return discounted_price
        discounted_price = total_price - (total_price * (int(discount_information[1]) / 100))
        return discounted_price

    def apply_discount(self, code):
        """
        Applies a discount to the user's total price if valid.

        Args:
            code (str): The discount code to apply.

        Returns:
            bool: True if the discount is applied successfully.

        Raises:
            ValueError: If the discount code has already been used or is invalid.
        """
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
            raise RuntimeError('Invalid code!')

    def flush_basket(self):
        """
        Clears the user's basket from Redis.

        Returns:
            bool: True if the basket is flushed successfully; otherwise False.
        """
        try:
            self.__class__.__client.delete(f"user:{self.user}")
            return True
        except Exception:
            return False

    def create_order(self):
        """
        Creates an order from the user's basket data.

        Returns:
            bool: True if the order is created successfully.

        Raises:
            ValueError: If the basket is incomplete.
        """
        basket_copy = self.display_basket().copy()
        user = get_user_model().objects.get(id=self.user)
        order = Order.objects.create(user=user)

        if 'address' in basket_copy:
            order.address = self.get_address(int(basket_copy['address']))
            order.save()
            del basket_copy['address']

        if 'price_after_discount' not in basket_copy:
            raise ValueError("Basket is not completed yet")

        order.total_price = basket_copy['price_after_discount']
        order.save()
        del basket_copy['price_after_discount']
        del basket_copy['total_price']
        #
        receipt = self.get_receipt(basket_copy)
        order.product_list = receipt
        order.save()

        self.flush_basket()
        return True

    def get_address(self, id):
        """
        Retrieves the full address associated with the given ID.

        Args:
            id (int): The ID of the address.

        Returns:
            str: The full address as a string.
        """
        address = Address.objects.get(id=id)
        return address.full_address

    def validate_basket(self):
        """
        Validates if the basket contains both address and payment amount.

        Raises:
            ValidationError: If the basket is incomplete.

        Returns:
            bool: True if the basket is valid, otherwise raises ValidationError.
        """
        if self.__class__.__client.hexists(f"user:{self.user}", "address"):
            return True
        raise ValidationError("Basket is not complete!")

    def get_each_product_information_and_make_receipt(self, basket):
        """
        Args:
            basket:
        Returns:
            final receipt (a dictionary containing all product details)
        """
        receipt = {}
        for key, value in basket.items():
            product_name = key
            product_obj = Product.objects.get(name=product_name)
            product_id = product_obj.id
            product_slug = product_obj.slug
            product_price = product_obj.price
            quantity = int(value)
            total_price = product_price * quantity


            receipt[product_id] = self.make_receipt(
                product_name=product_name,
                slug=product_slug,
                price=product_price,
                quantity=quantity,
                total_price=total_price
            )
        return receipt

    @staticmethod
    def make_receipt(product_name, slug, price, quantity, total_price):
        """
        Args:
            product: Product ID
            product_name: Name of the product
            slug: Product slug
            price: Unit price of the product
            quantity: Quantity of the product
            total_price: Total price for the quantity

        Returns:
            A dictionary representing the receipt for a single product
        """
        return {
            "name": product_name,
            "slug": slug,
            "price": price,
            "quantity": quantity,
            "total_price": total_price
        }


    def get_receipt(self, basket):
        """
        Args:
            basket:
        Returns
            final receipt
        """
        result = self.get_each_product_information_and_make_receipt(basket)
        return result
