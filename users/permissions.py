from rest_framework.permissions import BasePermission

class IsBuxgalterUser(BasePermission):
    """
    Custom permission to allow only users with position 'bugalter' to create users with position 'omborchi'.
    """
    def has_permission(self, request, view):
        return request.user.position == 0


class IsOmborchiUser(BasePermission):
    """
    Custom permission to allow only users with position 'bugalter' to create users with position 'omborchi'.
    """
    def has_permission(self, request, view):
        return request.user.position == 1
