from django.http import HttpRequest
from django.shortcuts import render
from rest_framework.response import Response

from rest_framework import status
from rest_framework.viewsets import ViewSet
from rest_framework_simplejwt.authentication import JWTAuthentication

from authentication.permissions import IsOwner
from checkout.serializers import BasketSubmitSerializer
from order.models import Basket


# Create your views here.
class OrderCheckoutViewSet(ViewSet):
    permission_classes = [IsOwner]
    authentication_classes = [JWTAuthentication]
    user_receipt = {
        "address": None,
        "user_id": None,
        "sum": None,
        "editable": True
    }

    def is_editable(self):
        self.__class__.user_receipt["editable"] = False

    def list(self, request: HttpRequest, *args, **kwargs):
        bas = Basket.objects.get(customer=request.user.customer_profile.id)
        print(bas.receipt)
        try:
            basket = Basket.objects.get(customer=request.user.customer_profile.id)
            if bool(basket.receipt):
                return Response({"your order": basket.receipt})
            return Response({"message": "please choose an address"})
        except AttributeError:
            return Response({"message": "you dont have any profile please create an account first"})

    def create(self, request, *args, **kwargs):
        serializer = BasketSubmitSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "order successfully submitted!"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
