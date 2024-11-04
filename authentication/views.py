from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from django.http import HttpRequest
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from authentication.models import User, SellerProfile, Address
from authentication.seralizers import CustomerProfileSerializer, SellerProfileSerializer, AddressSerializer, \
    UserSerializer
from rest_framework.viewsets import ViewSet, GenericViewSet
from rest_framework import mixins
from .permissions import IsOwner


class CustomerViewSet(ViewSet):
    """
    ViewSet for managing customer user registrations.

    Attributes:
        queryset: The collection of User objects for the view.
        serializer_class: The serializer class to validate and serialize input data.
        permission_classes: Permissions applied to this view (AllowAny allows unrestricted access).
    """

    queryset = User.objects.all()
    serializer_class = CustomerProfileSerializer
    permission_classes = [AllowAny]

    def create(self, request):
        """
        Handles the creation of a new customer user.

        Args:
            request (HttpRequest): The HTTP request containing user data.

        Returns:
            Response: JSON response with user data or error details.
        """
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            try:
                user = serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            except IntegrityError as e:
                if 'unique constraint' in e.args[0]:
                    return Response({"error": "Username or email already exists"}, status=status.HTTP_409_CONFLICT)
                return Response({"error": "Username or email already exists"},
                                status=status.HTTP_409_CONFLICT)
            except Exception as e:
                return Response({"error": "An error occurred while creating the user"},
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response({'errors': serializer.errors, 'message': 'Input error: not valid'},
                        status=status.HTTP_400_BAD_REQUEST)


class SellerViewSet(ViewSet):
    """
    ViewSet for managing seller user registrations.

    Attributes:
        serializer_class: The serializer class to validate and serialize seller input data.
        permission_classes: Permissions applied to this view (AllowAny allows unrestricted access).
        authentication_classes: Classes used for authentication (JWTAuthentication for token-based auth).
    """

    serializer_class = SellerProfileSerializer
    permission_classes = [AllowAny]
    authentication_classes = [JWTAuthentication]

    def create(self, request):
        """
        Handles the creation of a new seller user.

        Args:
            request (HttpRequest): The HTTP request containing seller data.

        Returns:
            Response: JSON response with seller data or error details.
        """
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
    """
    ViewSet for managing user profiles.

    Attributes:
        authentication_classes: Classes used for authentication (JWTAuthentication for token-based auth).
        queryset: The collection of User objects for the view.
        serializer_class: The serializer class to validate and serialize user data.
        lookup_field: The field used for looking up users (UUID in this case).
    """

    authentication_classes = [JWTAuthentication]
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'uuid'

    def get_permissions(self):
        """
        Returns permissions for different actions.

        Returns:
            list: The list of permission classes applicable for the current action.
        """
        if self.action == 'list':
            return [IsAdminUser()]
        if self.action == 'retrieve':
            return [IsAdminUser(), IsOwner()]
        return super().get_permissions()

    def get_queryset(self):
        """
        Retrieves the queryset for the user profiles with optional filtering.

        Returns:
            queryset: The filtered queryset based on the is_seller parameter in the request.
        """
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
        """
        Handles GET requests to list users.

        Args:
            request (HttpRequest): The HTTP request object.

        Returns:
            Response: JSON response containing a list of users.
        """
        return super(UsersProfileViewSet, self).list(request)

    def retrieve(self, request, uuid=None):
        """
        Handles GET requests to retrieve a specific user by UUID.

        Args:
            request (HttpRequest): The HTTP request object.
            uuid (str): The UUID of the user to retrieve.

        Returns:
            Response: JSON response containing the user data, or an error message if not found.
        """

        try:
            user = User.objects.get(uuid=uuid)
            self.check_object_permissions(request, user)
            serializer = UserSerializer(user)
            return Response(serializer.data)
        except ObjectDoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

    def update(self, request, uuid=None):
        """
        Handles updating a seller's status; blocks a seller if they exist.

        Args:
            request (HttpRequest): The HTTP request object.
            uuid (str): The UUID of the seller to block.

        Returns:
            Response: JSON response indicating success or failure of the block action.
        """
        if bool(User.objects.get(uuid=uuid).is_seller):
            SellerProfile.objects.filter(user__uuid=uuid).update(is_blocked=True)
            return Response({"message": "User has been blocked successfully"}, status=status.HTTP_200_OK)
        return Response({"message": "User is not a seller"})


class UserAddressesViewSet(ViewSet):
    """
    ViewSet for managing user addresses.

    Attributes:
        authentication_classes: Classes used for authentication (JWTAuthentication for token-based auth).
    """

    authentication_classes = [JWTAuthentication]

    def get_permission(self):
        """
        Returns permissions for different actions based on user ownership and actions.

        Returns:
            list: The list of permission classes applicable for the current action.
        """
        if self.action == 'list':
            return [IsOwner()]
        if self.action == 'retrieve':
            return [IsOwner()]
        if self.action == 'create':
            return [AllowAny()]
        return super().get_permissions()

    def list(self, request: HttpRequest, user_uuid=None):
        """
        Lists all addresses associated with a specific user.

        Args:
            request (HttpRequest): The HTTP request object.
            user_uuid (str): The UUID of the user whose addresses are being retrieved.

        Returns:
            Response: JSON response containing a list of addresses.
        """
        queryset = Address.objects.filter(costumer__uuid=user_uuid)
        serializer = AddressSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, user_uuid=None, pk=None):
        """
        Retrieves a specific address by its primary key (pk) for a specific user.

        Args:
            request (HttpRequest): The HTTP request object.
            user_uuid (str): The UUID of the user who owns the address.
            pk (int): The primary key of the address.

        Returns:
            Response: JSON response with the address data or an error message if not found.
        """
        try:
            address = Address.objects.get(pk=pk, costumer__uuid=user_uuid)
            serializer = AddressSerializer(address)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Address.DoesNotExist:
            return Response({"error": "Address not found"}, status=status.HTTP_404_NOT_FOUND)

    def create(self, request: HttpRequest, *args, **kwargs):
        """
        Handles the creation of a new address for a user.

        Args:
            request (HttpRequest): The HTTP request containing address data.

        Returns:
            Response: JSON response with address data or error details.
        """
        serializer = AddressSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)