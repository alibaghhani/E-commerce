from .models import Product, Category
from rest_framework import serializers


class CategoryListActionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name', 'parent')


class CategoryDetailActionSerializer(serializers.ModelSerializer):
    product_amount = serializers.SerializerMethodField()
    parent_name = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ('name', 'parent', 'product_amount', 'parent_name')

    def get_product_amount(self, obj):
        return obj.product_category.count()

    def get_parent_name(self, obj):
        if obj.parent:
            return obj.parent.name
        return None


class ProductListActionSerializer(serializers.ModelSerializer):
    discounted_price = serializers.ReadOnlyField()

    class Meta:
        model = Product
        exclude = ('detail', 'category', 'slug', 'warehouse', 'seller')



class ProductDetailActionSerializer(serializers.ModelSerializer):
    discounted_price = serializers.ReadOnlyField()
    discount_amount = serializers.ReadOnlyField()

    class Meta:
        model = Product
        fields = '__all__'


class ProductCreateActionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'
