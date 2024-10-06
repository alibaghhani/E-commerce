from rest_framework.test import APITestCase, APIClient


class CustomerProfileTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()

        self.user_data = {
            "username": "test_user",
            "password": "test_password",
            "email": "test_email@gmail.com"
        }

    def test_create_costumer_profile(self):
