from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from django.http import HttpRequest
from django.shortcuts import render
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from authentication.models import User, CustomerProfile, SellerProfile, Address
from authentication.seralizers import CustomerProfileSerializer, SellerProfileSerializer, AddressSerializer, \
    UserSerializer
from rest_framework.viewsets import ModelViewSet, ViewSet
from .permissions import IsOwner


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
    serializer_class = SellerProfileSerializer
    permission_classes = [AllowAny]
    authentication_classes = [JWTAuthentication]

    def create(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            try:
                user = serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            except IntegrityError as e:
                print(e)
                if 'unique constraint' in e.args[0]:
                    return Response({"error": "Username or email already exists"},
                                    status=status.HTTP_400_BAD_REQUEST)
                return Response({"error": "Username or email already exists"},
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UsersProfileViewSet(ViewSet):
    authentication_classes = [JWTAuthentication]
    lookup_field = 'uuid'

    def get_permissions(self):
        if self.action == 'list':
            return [IsAdminUser()]
        if self.action == 'retrieve':
            return [IsAdminUser()]
        return super().get_permissions()

    def list(self, request):
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

    def retrieve(self, request, uuid=None):
        try:
            user = User.objects.get(uuid=uuid)
            serializer = UserSerializer(user)
            return Response(serializer.data)
        except ObjectDoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)


class UserAddressesViewSet(ViewSet):
    def get_permission(self):
        if self.action == 'list':
            return [IsAdminUser()]
        if self.action == 'retrieve':
            return [IsOwner()]
        if self.action == 'create':
            return [AllowAny()]
        return super().get_permissions()

    def list(self, request: HttpRequest, user_uuid=None):
        queryset = Address.objects.filter(costumer__uuid=user_uuid)
        serializer = AddressSerializer(queryset, many=True)
        return Response(serializer.data)
