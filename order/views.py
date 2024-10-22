from django.contrib.auth import get_user_model
from django.http import HttpRequest
from rest_framework import status
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from authentication.permissions import IsOwner
from rest_framework.viewsets import ViewSet, ModelViewSet
import json

from order.basket import BasketRedisAdapter


class BasketViewSet(ViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsOwner]
    user_model = get_user_model()

    def list(self, request: HttpRequest, *args, **kwargs):
        basket = BasketRedisAdapter(request=request)
        if basket.check_if_basket_exists():
            return Response({"basket":basket.display_basket()}, status=status.HTTP_200_OK)
        return Response({"message": "you dont have any basket!"}, status=status.HTTP_404_NOT_FOUND)

    def create(self, request, *args, **kwargs):
        product = request.POST.get("product_id")
        quantity = request.POST.get("quantity")

        if not product or not quantity:
            return Response({"message": "product_id and quantity must be specified."},
                            status=status.HTTP_400_BAD_REQUEST)

        if not str(product).isnumeric() or not str(quantity).isnumeric():
            return Response({"message": "enter valid inputs for product_id and quantity."},
                            status=status.HTTP_400_BAD_REQUEST)

        basket = BasketRedisAdapter(request=request, product=product, quantity=quantity)

        try:
            basket.add_to_basket()
            return Response({"message": "Product added to basket."}, status=status.HTTP_201_CREATED)
        except ValueError as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, *args, **kwargs):
        product = request.data.get('product')
        quantity = request.data.get('quantity')
        assert str(quantity).isnumeric(), 'please enter a valid input'
        basket = BasketRedisAdapter(request=request, product=product, quantity=quantity)
        try:
            basket.update_basket()
            return Response({"message": "basket updated successfully"}, status=status.HTTP_200_OK)
        except ValueError as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)