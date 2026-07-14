from rest_framework import permissions


class IsModerator(permissions.BasePermission):


    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if not request.user.is_staff:
            return False


        if request.method == 'POST':
            return False

        return True