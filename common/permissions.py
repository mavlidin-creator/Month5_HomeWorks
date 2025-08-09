from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsModerator(BasePermission):


    def has_permission(self, request, view):
        if request.method == "POST" and request.user.is_staff:
            return False
        if request.user.is_staff:
            return True
        return request.method in SAFE_METHODS

    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True
        return request.method in SAFE_METHODS
