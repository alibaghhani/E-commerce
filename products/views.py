from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpRequest
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from .models import Category, Product
from .serializers import CategoryDetailActionSerializer, CategoryListActionSerializer, ProductDetailActionSerializer, \
    ProductListActionSerializer, ProductCreateActionSerializer
from rest_framework.permissions import IsAdminUser, AllowAny
from rest_framework.viewsets import ModelViewSet
from authentication.permissions import IsSellerOrAdminOrReadOnly


class CategoryViewSet(ModelViewSet):
    """
    ViewSet for managing product categories.

    Attributes:
        serializer_class: The serializer used for category representations.
        queryset: The base queryset for category operations.
        lookup_field: The field used for looking up categories (ID in this case).
    """

    serializer_class = CategoryListActionSerializer
    queryset = Category.objects.all()
    lookup_field = 'id'

    def get_queryset(self):
        """
        Retrieves the list of categories, optionally filtering by parent category.

        Returns:
            queryset: All categories or only parent categories based on request parameters.
        """
        queryset = super().get_queryset()
        category = self.request.query_params.get('category', '').lower()
        if category == 'parents':
            queryset = queryset.filter(parent=None)
        return queryset

    def get_serializer_class(self, *args, **kwargs):
        """
        Returns appropriate serializer class based on current action.

        Returns:
            serializer_class: The serializer class corresponding to the action.
        """
        if self.action == 'list':
            return CategoryListActionSerializer
        if self.action == 'retrieve':
            return CategoryDetailActionSerializer
        else:
            return self.serializer_class

    def get_permissions(self):
        """
        Assigns permissions based on the action being performed.

        Returns:
            list: The list of permission classes applicable to the current action.
        """
        if self.action in ['create', 'update', 'destroy']:
            return [IsAdminUser()]
        return super().get_permissions()


class ProductViewSet(ModelViewSet):
    """
    ViewSet for managing products.

    Attributes:
        queryset: The base queryset for product operations.
        serializer_class: The serializer used for product representations.
        authentication_classes: List of authentication classes (JWT for token-based auth).
        lookup_field: The field used for looking up products (slug in this case).
        filter_backends: List of filter backends used for query filtering.
    """

    queryset = Product.objects.all()
    serializer_class = ProductListActionSerializer
    authentication_classes = [JWTAuthentication]
    lookup_field = 'slug'
    filter_backends = []

    def get_permissions(self):
        """
        Assigns permissions based on the action being performed, specifically for sellers and admins.

        Returns:
            list: The list of permission classes applicable to the current action.
        """
        if self.action in ['create', 'update']:
            return [IsSellerOrAdminOrReadOnly()]
        if self.action == 'destroy':
            return [AllowAny()]
        return super().get_permissions()

    def get_serializer_class(self, *args, **kwargs):
        """
        Returns appropriate serializer class based on current action.

        Returns:
            serializer_class: The serializer class corresponding to the action.
        """
        if self.action == 'list':
            return ProductListActionSerializer
        if self.action == 'retrieve':
            return ProductDetailActionSerializer
        else:
            return self.serializer_class

    def get_queryset(self):
        """
        Retrieves the list of products, optionally filtering by category and products query parameter.

        Returns:
            queryset: All products or filtered products based on request parameters.
        """
        queryset = super().get_queryset()
        products = self.request.query_params.get('products')
        if products == 'all':
            queryset = Product.objects.all()
        queryset = queryset.filter(category__id=self.kwargs['category_id'])
        return queryset

    def retrieve(self, request, category_id=None, slug=None, *args, **kwargs):
        """
        Retrieves a specific product by its slug.

        Args:
            request (HttpRequest): The HTTP request object.
            category_id (str): The ID of the product's category (if applicable).
            slug (str): The slug of the product to retrieve.

        Returns:
            Response: JSON response containing the product details or an error message if not found.
        """
        try:
            queryset = Product.objects.get(slug=slug)
            serializer = ProductDetailActionSerializer(queryset)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Product.DoesNotExist:
            return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)


class AllProductsViewSet(ModelViewSet):
    """
    ViewSet that allows access to all products with additional filtering options.

    Attributes:
        serializer_class: The serializer used for product representations.
        queryset: The base queryset for product operations.
        authentication_classes: List of authentication classes (JWT for token-based auth).
        lookup_field: The field used for looking up products (slug in this case).
    """

    serializer_class = ProductListActionSerializer
    queryset = Product.objects.all()
    authentication_classes = [JWTAuthentication]
    lookup_field = "slug"

    def get_permissions(self):
        """
        Assigns permissions based on the action being performed, specifically for sellers and admins.

        Returns:
            list: The list of permission classes applicable to the current action.
        """
        if self.action in ['retrieve', 'update', 'create']:
            return [IsSellerOrAdminOrReadOnly()]
        if self.action == 'list':
            return [AllowAny()]
        return super().get_permissions()

    def get_serializer_class(self, *args, **kwargs):
        """
        Returns appropriate serializer class based on current action.

        Returns:
            serializer_class: The serializer class corresponding to the action.
        """
        if self.action == 'create':
            return ProductCreateActionSerializer
        if self.action in ['retrieve', 'destroy', 'update']:
            return ProductDetailActionSerializer
        else:
            return self.serializer_class

    def get_queryset(self):
        """
        Retrieves the list of products, applying filtering based on price range and order.

        Returns:
            queryset: Filtered products based on request parameters.
        """
        queryset = super().get_queryset()
        price = self.request.query_params.get('price')
        if price:
            if '-' in price:
                min_value = str(price.split('-')[0])
                max_value = str(price.split('-')[1])
                if min_value and max_value:
                    queryset = queryset.filter(
                        price__gte=int(min_value),
                        price__lte=int(max_value)
                    )
                if price[0] == '-':
                    queryset = queryset.filter(price__lte=int(price.split('-')[1]))
            if '-' not in price:
                queryset = queryset.filter(price__gte=int(price))

        order = self.request.query_params.get('order')
        if order is not None:
            fields = ['id', '-id', 'price', '-price', 'created_at', '-created_at']
            if order in fields:
                queryset = queryset.order_by(order)
            else:
                raise ValidationError({'error': f'Order field must be in {fields}'})

        return queryset

    def destroy(self, request: HttpRequest, *args, **kwargs):
        """
        Handles the deletion of a product. Allows deletion by sellers or superusers with a soft delete option.

        Args:
            request (HttpRequest): The HTTP request object.

        Returns:
            Response: JSON response indicating success or failure of the deletion operation.
        """
        product = Product.objects.get(slug=kwargs.get("slug"))
        user = get_user_model().objects.get(id=request.user.id)
        try:
            if user.is_seller:
                product.soft_delete()
                return Response({"message": "Product has been deleted successfully!"}, status=status.HTTP_200_OK)
            if request.user.is_superuser:
                product.delete()
                return Response({"message": "Product has been deleted successfully!"}, status=status.HTTP_200_OK)
        except ObjectDoesNotExist:
            return Response({"message": "Product does not exist!"}, status=status.HTTP_404_NOT_FOUND)
        return Response({"message": "You don't have permission to do this action!"})