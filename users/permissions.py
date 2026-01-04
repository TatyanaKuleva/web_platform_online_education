from rest_framework import permissions


class IsModerators(permissions.BasePermission):
    """Проверяет является ли пользователь Модератором."""

    def has_permission(self, request, view):
        return request.user.groups.filter(name="moderators").exists()


class IsOwner(permissions.BasePermission):
    """Проверяет является ли пользователь Владельцем"""

    def has_object_permission(self, request, view, obj):
        if obj.owner == request.user:
            return True
        return False


class IsUserOwner(permissions.BasePermission):
    """
    Позволяет редактировать объект только его владельцу,
    остальные могут только читать.
    """

    def has_object_permission(self, request, view, obj):
        # Разрешаем неавторизованное чтение (SAFE_METHODS = GET, HEAD, OPTIONS)
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.id == request.user.id
