from django.shortcuts import render
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.authentication import JWTAuthentication

from .serializers import BasketCreateSerializer
from rest_framework.viewsets import ModelViewSet
from .models import Basket


class BasketViewSet(ModelViewSet):
    permission_classes = [AllowAny]
    queryset = Basket.objects.all()
    serializer_class = BasketCreateSerializer
    authentication_classes = [JWTAuthentication]

    def get_queryset(self, *args, **kwargs):
        user = self.request.user
        if user.is_authenticated:
            return Basket.objects.filter(customer=user.customer_profile)
        return Basket.objects.none()

    def get_serializer_class(self):
        if self.action in ['create', 'update']:
            return BasketCreateSerializer
        return self.serializer_class
