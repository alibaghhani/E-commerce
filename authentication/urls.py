from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import CustomerViewSet

router = DefaultRouter()
router.register(
    r'customer/register',
    CustomerViewSet,
    basename='customer'
)

urlpatterns = [

]

urlpatterns += router.urls