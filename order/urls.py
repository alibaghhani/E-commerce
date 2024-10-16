from rest_framework.routers import DefaultRouter
from .views import BasketViewSet

router = DefaultRouter()
router.register(
    r'order',
    BasketViewSet,
    'order'
)

urlpatterns = []
urlpatterns += router.urls
