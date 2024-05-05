from rest_framework.permissions import BasePermission

class IsBuxgalterUser(BasePermission):
    """
    Custom permission to allow only users with position 'bugalter' to create users with position 'omborchi'.
    """
    def has_permission(self, request, view):
        # Check if the requesting user is 'bugalter'
        return request.user.position == 0  # Assuming 0 is the position for 'bugalter'
