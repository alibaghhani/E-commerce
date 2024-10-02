from django.db import IntegrityError
from django.shortcuts import render
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response

from authentication.models import User, CustomerProfile, SellerProfile
from authentication.seralizers import CustomerProfileSerializer, SellerProfileSerializer
from rest_framework.viewsets import ModelViewSet, ViewSet


class CustomerViewSet(ViewSet):
    queryset = User.objects.all()
    serializer_class = CustomerProfileSerializer
    permission_classes = [AllowAny]

    def create(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            try:
                user = serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            except IntegrityError as e:
                print(e)
                if 'unique constraint' in e.args[0]:
                    return Response({"error": "Username or email already exists"}, status=status.HTTP_400_BAD_REQUEST)
                return Response({"error": "Username or email already exists"},
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SellerViewSet(ViewSet):
    queryset = User.objects.all()
    serializer_class = SellerProfileSerializer
    permission_classes = [AllowAny]

    def create(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            try:
                user = serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            except IntegrityError as e:
                print(e)
                if 'unique constraint' in e.args[0]:
                    return Response({"error": "Username or email already exists"}, status=status.HTTP_400_BAD_REQUEST)
                return Response({"error": "Username or email already exists"},
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
