import uuid

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase
from authentication.models import User, SellerProfile, CustomerProfile
from authentication.seralizers import UserSerializer
from products.models import Category
from products.serializers import CategoryListActionSerializer


class ProductAndCategoryTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin_user_data = {
            "username": "TestUsername",
            "email": "TestEmail@gmail.com",
            "password": "TestUsernameP@ssword",
            "uuid": uuid.uuid4(),
        }
        self.regular_user_data = {
            "username": "TestRegularUsername",
            "email": "TestRegularEmail@gmail.com",
            "password": "TestUsernameP@ssword",
            "uuid": uuid.uuid4(),
        }

        category_obj = Category.objects.create(name="parent")

        self.category_data = {
            "name": "tes-tcategory",
            "parent": category_obj.id
        }
        self.user = User.objects.create_user(**self.admin_user_data)
        self.admin = User.objects.create_superuser(**self.regular_user_data)

        self.category_base_url = reverse('categories-list')

    def test_admin_can_see_list_of_products(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(self.category_base_url)
        queryset = Category.objects.all()
        serializer = CategoryListActionSerializer(queryset, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_regular_user_can_see_categories(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.category_base_url)
        queryset = Category.objects.all()
        serializer = CategoryListActionSerializer(queryset, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_admin_can_create_category_instance(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.post(self.category_base_url, self.category_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_regular_user_can_create_category_instance(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.category_base_url, self.category_data, format='json')
        self.assertNotEqual(response.data, status.HTTP_201_CREATED)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
