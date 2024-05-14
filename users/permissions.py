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

class CanUpdateOmborchi(BasePermission):
    """
    Custom permission to allow omborchi to update their own data,
    and allow buxgalter to update any omborchi data.
    """

    def has_object_permission(self, request, view, obj):
        # If the user is buxgalter, allow the update
        if request.user.position == 0:
            return True
        # If the user is omborchi and trying to update their own data, allow the update
        elif request.user == obj:
            return True
        return False
