from django.http import HttpRequest
from rest_framework import serializers
from .models import Basket
from products.models import Product


class BasketCreateSerializer(serializers.Serializer):
    product = serializers.IntegerField()
    quantity = serializers.IntegerField(max_value=10)

    def create(self, validated_data):
        request: HttpRequest = self.context.get('request')
        product = validated_data['product']
        quantity = validated_data['quantity']

        if request and hasattr(request, 'user'):
            customer = request.user.customer_profile

        product_entry = {"id": product, "quantity": quantity}

        basket, created = Basket.objects.get_or_create(customer=customer)

        if not basket.products_list:
            basket.products_list = [product_entry]
        else:
            product_found = False
            for items in basket.products_list:
                if items['id'] == product:
                    items['quantity'] += quantity
                    product_found = True
                    break

            if not product_found:
                basket.products_list.append(product_entry)

        basket.save()
        return basket