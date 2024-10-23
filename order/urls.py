from django.urls import path, include
from rest_framework.routers import DefaultRouter,SimpleRouter
from order.views import BasketViewSet,BasketSubmitViewSet
from rest_framework_nested import routers
router = DefaultRouter()
router.register(
    r'basket',
    BasketViewSet,
    'basket'
)


router.register(
    r'submit_basket',
    BasketSubmitViewSet,
    'submit_basket'

)


urlpatterns = [

]
urlpatterns += router.urls
