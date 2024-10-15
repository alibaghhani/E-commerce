from django.core.exceptions import ObjectDoesNotExist, ValidationError
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
from rest_framework.viewsets import ModelViewSet, ViewSet, GenericViewSet
from rest_framework import mixins
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
                print(e.args)
                if 'unique constraint' in e.args[0]:
                    return Response({"error": "Username or email already exists"}, status=status.HTTP_409_CONFLICT)
                return Response({"error": "Username or email already exists"},
                                status=status.HTTP_409_CONFLICT)
            except Exception as e:
                return Response({"error": "An error occurred while creating the user"},
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response({'errors': serializer.errors, 'message': 'input error: not valid'},
                        status=status.HTTP_400_BAD_REQUEST)


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
                if 'unique constraint' in e.args[0]:
                    return Response({"error": "Username or email already exists"},
                                    status=status.HTTP_400_BAD_REQUEST)
                return Response({"error": "Username or email already exists"},
                                status=status.HTTP_409_CONFLICT)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UsersProfileViewSet(GenericViewSet, mixins.ListModelMixin):
    authentication_classes = [JWTAuthentication]
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'uuid'

    def get_permissions(self):
        if self.action == 'list':
            return [IsAdminUser()]
        if self.action == 'retrieve':
            return [IsAdminUser(), IsOwner()]
        return super().get_permissions()

    def get_queryset(self):
        queryset = super().get_queryset()
        is_seller = self.request.query_params.get('is_seller')
        if is_seller:
            if is_seller == 'True':
                queryset = queryset.filter(is_seller=is_seller)
            elif is_seller == 'False':
                queryset = queryset.filter(is_seller=False)
            else:
                queryset = queryset.all()
        return queryset

    def list(self, request, *args, **kwargs):
        return super(UsersProfileViewSet, self).list(request)

    def retrieve(self, request, uuid=None):

        try:
            user = User.objects.get(uuid=uuid)
            self.check_object_permissions(request, user)
            serializer = UserSerializer(user)
            return Response(serializer.data)
        except ObjectDoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

    def update(self, request, uuid=None):
        if bool(User.objects.get(uuid=uuid).is_seller):
            SellerProfile.objects.filter(user__uuid=uuid).update(is_blocked=True)
            return Response({"message": "user has been blocked successfully"}, status=status.HTTP_200_OK)
        return Response({"message": "user is not seller"})


class UserAddressesViewSet(ViewSet):
    authentication_classes = [JWTAuthentication]

    def get_permission(self):
        if self.action == 'list':
            return [IsOwner()]
        if self.action == 'retrieve':
            return [IsOwner()]
        if self.action == 'create':
            return [AllowAny()]
        return super().get_permissions()

    def list(self, request: HttpRequest, user_uuid=None):
        queryset = Address.objects.filter(costumer__uuid=user_uuid)
        serializer = AddressSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, user_uuid=None, pk=None):
        try:
            address = Address.objects.get(pk=pk, costumer__uuid=user_uuid)
            serializer = AddressSerializer(address)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Address.DoesNotExist:
            return Response({"error": "Address not found"}, status=status.HTTP_404_NOT_FOUND)

    def create(self, request: HttpRequest, *args, **kwargs):
        serializer = AddressSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
