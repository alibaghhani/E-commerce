from rest_framework.routers import DefaultRouter

from checkout.views import OrderCheckoutViewSet

router = DefaultRouter()

router.register(
    r'submit_address',
    OrderCheckoutViewSet,
    'submit_order'
)

urlpatterns = []
urlpatterns += router.urls