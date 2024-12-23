from requests import Response
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import BasePermission, SAFE_METHODS

from order.basket import BasketAndOrderRedisAdapter


class IsOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        if obj.id == request.user.id:
            return True
        if request.user.is_superuser:
            return True
        return False


class IsSellerOrAdminOrReadOnly(BasePermission):

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return request.user.is_authenticated and request.user.is_seller or request.user.is_superuser

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return obj.seller == request.user

class ValidateBasket(BasePermission):
    def has_permission(self, request, view):
        basket = BasketAndOrderRedisAdapter(request=request)
        try:
            basket.validate_basket()
            return True
        except ValidationError:
            return False
        except Exception as e:
            print(e)
            return False
