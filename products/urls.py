from django.urls import path, include
from rest_framework.routers import SimpleRouter, DefaultRouter
from .views import CategoryViewSet, ProductViewSet, AllProductsViewSet
from rest_framework_nested import routers


router = SimpleRouter()
router.register(
    r'categories',
    CategoryViewSet,
    basename='categories'
)


product_router = routers.NestedSimpleRouter(
    router,
    r'categories',
    lookup='category'
)

product_router.register(
    r'products',
    ProductViewSet,
    basename='category-products'
)


products_router = DefaultRouter()
products_router.register(
    r'products',
    AllProductsViewSet,
    'product'
)

urlpatterns = [
    path('', include(router.urls)),
    path('', include(product_router.urls))
]
urlpatterns += products_router.urls