from http.client import HTTPResponse

from django.contrib.auth import get_user_model
from django.http import HttpRequest
from rest_framework.permissions import BasePermission, SAFE_METHODS
from urllib3 import request


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
        print('this method has been called has object permission')
        if request.method in SAFE_METHODS:
            return True
        return obj.seller == request.user
