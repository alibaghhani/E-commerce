from rest_framework.routers import DefaultRouter
from .views import BasketViewSet

router = DefaultRouter()
router.register(
    r'basket',
    BasketViewSet,
    'basket'
)

urlpatterns = []
urlpatterns += router.urls
