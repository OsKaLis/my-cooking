from rest_framework import permissions


class CreateUsers(permissions.BasePermission):
    message = 'Для выполнения данной операции необходимы права администратора!'

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return (request.user and request.user.is_staff)


class ChangePasswordUsers(permissions.BasePermission):
    message = 'Для выполнения данной операции необходимы быдь авторизованым!'

    def has_permission(self, request, view):
        if request.method == 'PATCH':
            return True
        return (request.user.is_authenticated and request.user.is_staff)


class DeletingTokenUsers(permissions.BasePermission):
    message = 'Для выполнения данной операции необходимы быдь авторизованым!'

    def has_permission(self, request, view):
        if request.method == 'DELETE':
            return True
        return (request.user.is_authenticated and request.user.is_staff)
