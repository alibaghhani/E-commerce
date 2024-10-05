from django.urls import path, include
from rest_framework.routers import DefaultRouter, SimpleRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView
from rest_framework_nested import routers
from .views import CustomerViewSet, SellerViewSet, UsersProfileViewSet, UserAddressesViewSet

router = SimpleRouter()
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

router.register(
    r'users',
    UsersProfileViewSet,
    basename='customer-profile'
)

address_router = routers.NestedSimpleRouter(
    router,
    r'users',
    lookup='user'
)

address_router.register(
    r'addresses',
    UserAddressesViewSet,
    basename='user-addresses'
)

urlpatterns = [
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('', include(router.urls)),
    path('', include(address_router.urls))
    ]


