from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase
from authentication.models import User, SellerProfile, CustomerProfile
from authentication.seralizers import UserSerializer
from products.models import Category


class ProductAndCategoryTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user_data = {
            "username": "TestUsername",
            "email": "TestEmail@gmail.com",
            "password": "TestUsernameP@ssword",
        }
        self.category_base_url = reverse('categories-list')

    def test_admin_can_see_list_of_products(self):
        admin = User.objects.create_superuser(**self.user_data)
        self.client.force_authenticate(user=admin)
        response = self.client.get(self.category_base_url)
        queryset = Category.objects.all()
        serializer = UserSerializer(queryset, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_regular_user_can_see_categories(self):
        user = User.objects.create_user(**self.user_data)
        self.client.force_authenticate(user=user)
        response = self.client.get(self.category_base_url)
        queryset = Category.objects.all()
        serializer = UserSerializer(queryset, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)
