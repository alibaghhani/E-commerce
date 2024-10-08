from django.shortcuts import render
from rest_framework.viewsets import GenericViewSet
from .models import Category, Product
from .serializers import CategoryDetailActionSerializer, CategoryListActionSerializer
from rest_framework.permissions import IsAdminUser, AllowAny
from rest_framework.viewsets import ModelViewSet


# Create your views here.

class CategoryViewSet(ModelViewSet):
    serializer_class = CategoryListActionSerializer
    queryset = Category.objects.all()

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
        return [AllowAny()]
