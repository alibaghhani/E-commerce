from rest_framework import serializers

from authentication.models import Address
from order.models import Basket


class BasketSubmitSerializer(serializers.Serializer):
    address = serializers.IntegerField()


    def validate_address(self, value):
        user = self.context['request'].user
        address = Address.objects.get(id=value)
        if not address.costumer.id == user.id:
            raise serializers.ValidationError("You can only choose your own addresses.")
        return value

    def create(self, validated_data):
        user_id = self.context.get('request').user.customer_profile.id
        basket = Basket.objects.get(customer=user_id)
        print(f"=======> before updating{basket.receipt}")
        basket.receipt["address"] = validated_data["address"]
        basket.receipt["total_price"] = basket.sum_of_prices
        basket.receipt["date_created"] = basket.created_at
        print(basket.sum_of_prices)
        print(f"========> after updating{basket.receipt}")
        # return basket.receipt

