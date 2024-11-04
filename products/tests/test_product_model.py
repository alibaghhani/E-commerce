from django.test import TestCase
from authentication.models import User, SellerProfile
from products.models import Product, Category

class ProductAndCategoryTestCase(TestCase):
    """
    Test case for verifying the functionality of product and category models.

    This includes tests for creating products and categories,
    ensuring their correctness and validating model methods.
    """

    def setUp(self):
        """
        Sets up the test environment by creating a test user, seller profile,
        category, and product data for the tests.
        """
        self.user = User.objects.create(
            email='testemail@gmail.com',
            username='testUsername',
            password='TestP@assword',
            is_seller=True
        )
        self.seller = SellerProfile.objects.create(
            user=self.user
        )
        self.category = Category.objects.create(
            name='testcategory'
        )

        self.product_data = {
            "name": "Sample Product",
            "price": 1500,
            "detail": "This is a sample product with detailed description.",
            "category": self.category,
            "warehouse": 100,
            "slug": "sample-product",
            "seller": self.seller
        }

    def test_create_product(self):
        """
        Test that a product can be created successfully and its properties are correct.
        """

        product = Product.objects.create(**self.product_data)
        self.assertEqual(self.product_data['price'], product.price)
        self.assertEqual(product.__str__(), product.name)

    def test_create_category(self):
        """
        Test that a category can be created successfully and its properties are correct.
        """

        category = Category.objects.create(name='testcategory')
        category.get_all_parents()
        self.assertEqual(category.__str__(), category.name)
        self.assertIn(category, category.get_all_parents())