from django.urls import path
from .views import payment_gateway
urlpatterns = [
    path("payment/", payment_gateway)
]

