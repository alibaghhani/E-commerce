from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import CustomerViewSet, SellerViewSet

router = DefaultRouter()
router.register(
    r'customer/register',
    CustomerViewSet,
    basename='customer'
)

router.register(
    r'seller/register',
    SellerViewSet,
    basename='seller'
)

urlpatterns = []

urlpatterns += router.urls
