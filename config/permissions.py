from rest_framework.permissions import BasePermission


class IsStaffUser(BasePermission):
    """Only allow staff (is_staff=True) users."""

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_staff
