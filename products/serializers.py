from .models import Product, Category
from rest_framework import serializers


class CategoryListActionSerializer(serializers.ModelSerializer):
    """
    Serializer for listing categories with basic information.

    Attributes:
        Meta: Configures the serializer to the Category model and specifies the fields included in the serialized output.
    """

    class Meta:
        model = Category
        fields = ('id', 'name', 'parent')


class CategoryDetailActionSerializer(serializers.ModelSerializer):
    """
    Serializer for detailed category information, including product count and parent category name.

    Attributes:
        product_amount: A computed field for the number of products in the category.
        parent_name: A computed field for the name of the parent category.

    Methods:
        get_product_amount: Returns the count of products associated with the category.
        get_parent_name: Returns the name of the parent category if it exists.
    """

    product_amount = serializers.SerializerMethodField()
    parent_name = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ('name', 'parent', 'product_amount', 'parent_name')

    def get_product_amount(self, obj):
        """
        Computes the number of products in this category.

        Args:
            obj (Category): The category instance.

        Returns:
            int: The count of products in the category.
        """
        return obj.product_category.count()

    def get_parent_name(self, obj):
        """
        Retrieves the name of the parent category.

        Args:
            obj (Category): The category instance.

        Returns:
            str or None: The name of the parent category, or None if no parent exists.
        """
        if obj.parent:
            return obj.parent.name  # Return name of the parent if it exists
        return None  # No parent, so return None


class ProductListActionSerializer(serializers.ModelSerializer):
    """
    Serializer for listing products with basic information and discounted price.

    Attributes:
        discounted_price: A read-only field that calculates the discounted price of the product.

    Attributes:
        Meta: Configures the serializer to the Product model and specifies fields to exclude from serialization.
    """

    discounted_price = serializers.ReadOnlyField()

    class Meta:
        model = Product
        exclude = ('detail', 'category', 'slug', 'warehouse', 'seller')


class ProductDetailActionSerializer(serializers.ModelSerializer):
    """
    Serializer for detailed product information, including all fields of the Product model.

    Attributes:
        discounted_price: A read-only field representing the discounted price.
        discount_amount: A read-only field that shows the amount discounted from the product price.

    Attributes:
        Meta: Configures the serializer to the Product model and specifies all fields to include in serialization.
    """

    discounted_price = serializers.ReadOnlyField()
    discount_amount = serializers.ReadOnlyField()

    class Meta:
        model = Product
        fields = '__all__'


class ProductCreateActionSerializer(serializers.ModelSerializer):
    """
    Serializer for creating new product instances.

    Attributes:
        Meta: Configures the serializer to the Product model and specifies fields to include in serialization.
    """

    class Meta:
        model = Product
        fields = '__all__'