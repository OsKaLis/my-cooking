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
