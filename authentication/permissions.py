from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        if obj.id == request.user.id:
            return True
        return False


class IsSellerOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        if obj.seller == request.user.id:
            return True
        if obj.seller == request.user.id:
            return True
        return False
