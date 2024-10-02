from django.contrib.auth.hashers import make_password
from django.test import TestCase

from authentication.models import User, SellerProfile, CustomerProfile


# Create your tests here.
class UsersAndProfilesTestCase(TestCase):
    """
    Test cases for SellerProfile model.

    """

    def setUp(self):
        """
        Create a seller and a customer user
        """
        self.seller_data = {
            "email": "testseller@gmail.com",
            "username": "test_seller_user",
            "password": "test12345678",
            "is_seller": True,
            "is_superuser": False,
            "is_staff": False
        }
        self.customer_data = {
            "email": "testcustomer@gmail.com",
            "username": "test_customer_user",
            "password": "test12345678",
            "is_seller": False,
            "is_superuser": False,
            "is_staff": False
        }
        self.seller = User.objects.create(**self.seller_data)
        self.customer_user = User.objects.create(**self.customer_data)

    def test_create_seller_profile(self):
        """
        Test creating a SellerProfile with a valid seller user.
        """
        seller = SellerProfile.objects.create(first_name='test seller', user=self.seller)
        self.assertEqual(seller.first_name, 'test seller')
        self.assertEqual(True, self.seller.is_seller)
        self.assertNotEqual(True, self.seller.is_superuser)
        self.assertNotEqual(True, self.seller.is_staff)

    def test_create_customer_profile(self):
        """
        Test creating a CustomerProfile with a valid customer user.
        """
        customer = CustomerProfile.objects.create(first_name='test customer', user=self.customer_user)
        self.assertEqual(customer.first_name, 'test customer')
        self.assertNotEqual(True, self.customer_user.is_seller)
        self.assertNotEqual(True, self.customer_user.is_superuser)
        self.assertNotEqual(True, self.customer_user.is_staff)

    def test_hash_password(self):
        """
        Test password hashing
        """
        self.assertNotEqual(self.customer_data['password'], self.customer_user.password)
