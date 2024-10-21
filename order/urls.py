from rest_framework.routers import DefaultRouter

from order.views import BasketViewSet

router = DefaultRouter()
router.register(
    r'basket',
    BasketViewSet,
    'basket'
)
urlpatterns = []
urlpatterns += router.urls