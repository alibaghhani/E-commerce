from django.http import Http404
from django.shortcuts import render
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.generics import ListAPIView, RetrieveDestroyAPIView, GenericAPIView
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
        is_seller = self.request.query_params.get('category')
        if is_seller == 'parents':
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

    def get_permissions(self):
        if self.action == 'create':
            return [IsSellerOrAdminOrReadOnly()]
        if self.action == 'update':
            return [IsSellerOrAdminOrReadOnly()]
        if self.action == 'destroy':
            return [IsSellerOrAdminOrReadOnly()]
        return super().get_permissions()

    def get_serializer_class(self, *args, **kwargs):
        if self.action == 'list':
            return ProductListActionSerializer
        if self.action == 'retrieve':
            return ProductDetailActionSerializer
        else:
            return self.serializer_class

    def get_queryset(self):
        print(self.kwargs)
        queryset = super().get_queryset()
        products = self.request.query_params.get('products')
        if products == 'all':
            queryset = Product.objects.all()
        queryset = queryset.filter(category__id=self.kwargs['category_id'])
        return queryset

    # def list(self, request, category_id=None, *args, **kwargs):
    #     queryset = Product.objects.filter(category__id=category_id)
    #     serializer = ProductListActionSerializer(queryset, many=True)
    #     return Response(serializer.data, status=status.HTTP_200_OK)

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

    def get_permissions(self):
        if self.action in ['retrieve', 'delete', 'update']:
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
