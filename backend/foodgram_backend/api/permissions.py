from rest_framework import permissions


class ProfileReadOnly(permissions.IsAuthenticated):
    """Для просмотра профиль и создания пользователя."""

    def has_permission(self, request, view):
        return (
            view.action in ['create', 'retrieve']
            or (request.user.is_authenticated and request.user.is_staff)
        )


class AuthenticatedOrReadOnly(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        if view.action in ['create', 'update', 'destroy']:
            return request.user.is_authenticated
        return True


class IsAdminUserOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(
            request.user.is_authenticated
            and request.user.is_staff
        )


"""
class VerificationAuthorAcceptance(permissions.BasePermission):
    message = 'К сожалению вы не автор рицепта.'

    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or obj.author == request.user
        )
"""
