import uuid
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase
from authentication.models import User, SellerProfile, CustomerProfile
from authentication.seralizers import UserSerializer
from products.models import Category
from products.serializers import CategoryListActionSerializer


class ProductAndCategoryTestCase(APITestCase):
    """
    Test case for verifying the behavior of product and category related endpoints.

    This includes tests for user permissions, creating categories, listing categories,
    and filtering categories based on the parent-child relationship.
    """

    def setUp(self):
        """
        Sets up the test environment by creating a test client and necessary user
        and category instances for the tests.
        """
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


        category_obj = Category.objects.create(name="test-category")


        self.category_data = {
            "name": "tes-tcategory",
            "parent": category_obj.id
        }


        self.user = User.objects.create_user(**self.admin_user_data)
        self.admin = User.objects.create_superuser(**self.regular_user_data)


        self.category_base_url = reverse('categories-list')

    def test_admin_can_see_list_of_categories(self):
        """
        Test that an admin user can retrieve a list of categories.
        """
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(self.category_base_url)
        queryset = Category.objects.all()
        serializer = CategoryListActionSerializer(queryset, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_regular_user_can_see_categories(self):
        """
        Test that a regular user can retrieve a list of categories.
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.category_base_url)
        queryset = Category.objects.all()
        serializer = CategoryListActionSerializer(queryset, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_admin_can_create_category_instance(self):
        """
        Test that an admin user can create a new category.
        """
        self.client.force_authenticate(user=self.admin)
        response = self.client.post(self.category_base_url, self.category_data, format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_201_CREATED)

    def test_regular_user_can_create_category_instance(self):
        """
        Test that a regular user cannot create a new category.
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.category_base_url, self.category_data, format='json')
        self.assertNotEqual(response.data, status.HTTP_201_CREATED)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_filter_categories(self):
        """
        Test that categories can be filtered based on the parent-child relationship.
        """
        response = self.client.get(self.category_base_url, {"category": "parent"})
        self.assertEqual(None, response.data[0]['parent'])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'test-category')

    def test_users_can_see_category_detail(self):
        """
        Test that users can see details of a specific category.
        """
        category_detail_url = reverse('categories-detail', kwargs={"id": 1})
        response = self.client.get(category_detail_url)
        self.assertNotEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['name'], 'test-category')