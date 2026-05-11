from rest_framework.permissions import BasePermission, SAFE_METHODS


ROLE_GUEST = 'guest'
ROLE_USER = 'user'
ROLE_BUSINESS = 'business'
ROLE_ADMIN = 'admin'


def _is_authenticated_user(user):
    return bool(user and user.is_authenticated)


def _account_type(user):
    return getattr(user, 'account_type', None)


class IsAdminAccount(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        return bool(
            _is_authenticated_user(user)
            and (user.is_staff or _account_type(user) == ROLE_ADMIN)
        )


class IsBusinessAccount(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        return bool(
            _is_authenticated_user(user)
            and (user.is_staff or _account_type(user) in (ROLE_BUSINESS, ROLE_ADMIN))
        )


class IsAuthenticatedOrReadOnlyForCity(BasePermission):
    def has_permission(self, request, view):
        return request.method in SAFE_METHODS or _is_authenticated_user(request.user)


class IsUserAccount(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        return bool(
            _is_authenticated_user(user)
            and (user.is_staff or _account_type(user) in (ROLE_USER, ROLE_BUSINESS, ROLE_ADMIN))
        )


class IsSelfOrAdmin(BasePermission):
    def has_object_permission(self, request, view, obj):
        user = request.user
        if not _is_authenticated_user(user):
            return False
        return bool(user.is_staff or _account_type(user) == ROLE_ADMIN or getattr(obj, 'id', None) == user.id)
