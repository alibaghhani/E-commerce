from django.db import IntegrityError
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from collections import ChainMap
import json
from authentication.models import User
from authentication.seralizers import UserSerializer


class CustomerProfileTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()

        self.user_data = {
            "email": "test_email@gmail.com",
            "username": "test_userJGJGJ",
            "password": "test_passwordGFG%^%&h",

        }
        self.customer_profile_data = {
            "first_name": "John",
            "last_name": "Doe"
        }

        self.base_url = reverse('customer-list')

    def test_create_costumer_profile(self):
        self.user_data.update(self.customer_profile_data)
        response = self.client.post(self.base_url, self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_if_IntegrityError_raises_properly(self):
        self.user_data.update(self.customer_profile_data)
        self.client.post(self.base_url, self.user_data, format='json')
        response = self.client.post(self.base_url, self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertNotEqual(response.status_code, status.HTTP_201_CREATED)


class SellerProfileTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user_data = {
            "email": "test_email@gmail.com",
            "username": "test_userJGJGJ",
            "password": "test_passwordGFG%^%&h",
            "is_seller": True
        }

        self.seller_data = {
            "first_name": "John",
            "last_name": "Doe",
            "company_name": "Test Company",
            "about_company": "This is a test company."
        }

        self.base_url = reverse('seller-list')

    def test_create_seller_profile(self):
        self.user_data.update(self.seller_data)
        response = self.client.post(self.base_url, self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_if_IntegrityError_raises_properly(self):
        self.user_data.update(self.seller_data)
        self.client.post(self.base_url, self.user_data, format='json')
        response = self.client.post(self.base_url, self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)


class UserTestCase(APITestCase):
    def setUp(self):

        client = APIClient()
        self.user_data = {
            "email": "TestEmail@gmail.com",
            "username": "test-username",
            "password": "TestPassw@rd"

        }

        self.base_url = reverse('customer-profile-list')

        self.user_model_queryset = User.objects.all()

    def test_is_admin_permission(self):
        admin = User.objects.create_superuser(**self.user_data)
        self.client.force_authenticate(user=admin)
        response = self.client.get(self.base_url)
        serializer = UserSerializer(self.user_model_queryset, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_user_can_see_others_profile(self):
        user = User.objects.create_user(**self.user_data)
        self.client.force_authenticate(user=user)
        response = self.client.get(self.base_url)
        serializer = UserSerializer(self.user_model_queryset, many=True)
        self.assertNotEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class AddressTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user_data = {
            "email": "TestEmail@gmail.com",
            "username": "test-username",
            "password": "TestPassw@rd"

        }

        self.address_data = {
            "province": "Tehran",
            "city": "Tehran",
            "street": "1st Golbarg",
            "house_number": 5,
            "full_address": "1st Golbarg, Narenjestan Blvd., Shams Abaad Ind.Town, Hasan Abaad Old Rd.",
            "alley": "test-alley",

        }

        # self.list_or_create_base_url = reverse('user-addresses-list')

    def test_create_address(self):
        user = User.objects.create_user(**self.user_data)
        address_url = reverse('user-addresses-list', kwargs={'user_uuid': user.uuid})
        self.client.force_authenticate(user=user)
        response = self.client.post(address_url, self.address_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # self.client.post(address_url, **)
