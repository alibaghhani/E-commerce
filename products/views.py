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
    serializer_class = CategoryListActionSerializer
    queryset = Category.objects.all()
    lookup_field = 'id'

    def get_queryset(self):
        queryset = super().get_queryset()
        category = self.request.query_params.get('category', '').lower()
        if category == 'parents':
            queryset = queryset.filter(parent=None)
        return queryset

    def get_serializer_class(self, *args, **kwargs):
        if self.action == 'list':
            return CategoryListActionSerializer
        if self.action == 'retrieve':
            return CategoryDetailActionSerializer
        else:
            return self.serializer_class

    def get_permissions(self):
        if self.action == 'create':
            return [IsAdminUser()]
        if self.action == 'update':
            return [IsAdminUser()]
        if self.action == 'destroy':
            return [IsAdminUser()]
        return super().get_permissions()




class ProductViewSet(ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductListActionSerializer
    authentication_classes = [JWTAuthentication]
    lookup_field = 'slug'
    filter_backends = []

    def get_permissions(self):
        if self.action in ['create','update']:
            return [IsSellerOrAdminOrReadOnly()]
        if self.action == 'destroy':
            return [AllowAny()]
        return super().get_permissions()

    def get_serializer_class(self, *args, **kwargs):
        if self.action == 'list':
            return ProductListActionSerializer
        if self.action == 'retrieve':
            return ProductDetailActionSerializer
        else:
            return self.serializer_class

    def get_queryset(self):
        queryset = super().get_queryset()
        products = self.request.query_params.get('products')
        if products == 'all':
            queryset = Product.objects.all()
        queryset = queryset.filter(category__id=self.kwargs['category_id'])
        return queryset



    def retrieve(self, request, category_id=None, slug=None, *args, **kwargs):
        try:
            queryset = Product.objects.get(slug=slug)
            serializer = ProductDetailActionSerializer(queryset)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Product.DoesNotExist:
            return Response({"error": "product not found"}, status=status.HTTP_404_NOT_FOUND)




class AllProductsViewSet(ModelViewSet):
    serializer_class = ProductListActionSerializer
    queryset = Product.objects.all()
    authentication_classes = [JWTAuthentication]
    lookup_field = "slug"

    def get_permissions(self):
        if self.action in ['retrieve', 'update', 'create']:
            return [IsSellerOrAdminOrReadOnly()]
        if self.action == 'list':
            return [AllowAny()]
        return super().get_permissions()

    def get_serializer_class(self, *args, **kwargs):
        if self.action == 'create':
            return ProductCreateActionSerializer
        if self.action in ['retrieve', 'destroy', 'update']:
            return ProductDetailActionSerializer
        else:
            return self.serializer_class

    def get_queryset(self):
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
                raise ValidationError({'error': f'order field must be in {fields}'})
        # if 'slug' in self.kwargs:
        #     queryset = queryset.filter(slug=self.kwargs.get('slug'))
        return queryset

    def destroy(self, request:HttpRequest, *args, **kwargs):

        product = Product.objects.get(slug=kwargs.get("slug"))
        user = get_user_model().objects.get(id=request.user.id)
        try:
            if user.is_seller:
                product.soft_delete()
                return Response({"message":"product has been deleted successfully!"},status=status.HTTP_200_OK)
            if request.user.is_superuser:
                product.delete()
                return Response({"message": "product has been deleted successfully!"},status=status.HTTP_200_OK)
        except ObjectDoesNotExist:
            return Response({"message":"product does not exists!"}, status=status.HTTP_404_NOT_FOUND)
        return Response({"message":"you dont have permission to do this act!"})



