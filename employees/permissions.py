from rest_framework import permissions


class IsAdministrator(permissions.BasePermission):
    """Только для группы 'administrator'."""

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.groups.filter(name="administrator").exists()
        )


class IsCaretaker(permissions.BasePermission):
    """Только для группы 'caretaker'."""

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.groups.filter(name="caretaker").exists()
        )


class IsAdministratorOrReadOnly(permissions.BasePermission):
    """Чтение — всем, изменение — только админам."""

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return (
            request.user
            and request.user.is_authenticated
            and request.user.groups.filter(name="administrator").exists()
        )


class CanManageWorkplace(permissions.BasePermission):
    """Перемещать между столами может админ ИЛИ смотритель."""

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.groups.filter(
            name__in=["administrator", "caretaker"]
        ).exists()
