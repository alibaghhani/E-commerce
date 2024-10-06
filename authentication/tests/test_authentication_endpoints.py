from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from collections import ChainMap


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
        print(self.user_data)
        response = self.client.post(self.base_url, self.user_data, format='json')
        print(dir(response))
        print(response.json)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


