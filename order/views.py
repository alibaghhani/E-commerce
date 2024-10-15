from django.shortcuts import render
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication

from products.models import Product
from .serializers import BasketCreateSerializer
from rest_framework.viewsets import ModelViewSet
from .models import Basket


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

    # def destroy(self, request, *args, **kwargs):
    #     product_id = kwargs.get('product_id')
    #     basket = Basket.objects.get(customer=request.user.id)
    #     print(basket.products_list)

    def create(self, request, *args, **kwargs):

        serializer = BasketCreateSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            product_id = serializer.validated_data['product']
            product = Product.objects.get(id=product_id)
            quantity = serializer.validated_data['quantity']
            if product.warehouse >= quantity:
                serializer.save()
                print(f"=====entered id{product_id}")
                print(f"=====entered quantity{quantity}")

                print(f"======product warehouse{product.warehouse}")
                print(f"======product name{product.name}")

                print(f"{product.warehouse - quantity}")
                Product.objects.filter(id=product_id).update(warehouse=product.warehouse - quantity)
            else:
                return Response(
                    {"message": "product's warehouse is lower than chosen quantity"},
                    status=status.HTTP_422_UNPROCESSABLE_ENTITY
                )
        return Response(serializer.errors)

    # def list(self, request, *args, **kwargs):
    #     basket = Basket.objects.get(customer=request.user.id)
