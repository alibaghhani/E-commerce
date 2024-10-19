from django.shortcuts import render
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication

from products.models import Product
from .serializers import BasketCreateSerializer
from rest_framework.viewsets import ModelViewSet
from .models import Basket
import logging

logger = logging.getLogger(__name__)


class BasketViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Basket.objects.all()
    serializer_class = BasketCreateSerializer
    authentication_classes = [JWTAuthentication]

    def get_queryset(self, *args, **kwargs):
        user = self.request.user
        if user.is_authenticated:
            return Basket.objects.filter(customer=user.customer_profile)
        return Basket.objects.none()

    def create(self, request, *args, **kwargs):
        serializer = BasketCreateSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            product_id = serializer.validated_data['product']
            product = Product.objects.get(id=product_id)
            quantity = serializer.validated_data['quantity']
            if product.warehouse >= quantity:
                serializer.save()
                Product.objects.filter(id=product_id).update(warehouse=product.warehouse - quantity)
            else:
                return Response(
                    {"message": "product's warehouse is lower than chosen quantity"},
                    status=status.HTTP_422_UNPROCESSABLE_ENTITY
                )
        return Response(serializer.errors)

    def list(self, request, *args, **kwargs):
        customer_id = request.user.customer_profile.id
        basket = Basket.objects.get(customer__id=customer_id)
        products_ids = [item['id'] for item in basket.products_list]
        products_name = [Product.objects.get(id=i).name for i in products_ids]
        print(products_name)
        display_basket = {}
        if products_name:
            for i in products_name:
                display_basket.update(
                    {i: item['quantity'] for item in basket.products_list if
                     item['id'] in [Product.objects.get(name=i).id]}
                )
                print(request.user.customer_profile.id)
                print(display_basket)
        else:
            return Response({"message": "your basket is empty"})
        return Response({"your basket": display_basket})
