from rest_framework import permissions


def is_admin_user(user) -> bool:
    return bool(
        user
        and user.is_authenticated
        and (user.is_superuser or user.is_staff or getattr(user, "user_type", "") == "admin")
    )


def is_company_user(user) -> bool:
    return bool(user and user.is_authenticated and getattr(user, "user_type", "") == "company")


def is_normal_user(user) -> bool:
    return bool(user and user.is_authenticated and getattr(user, "user_type", "") == "normal")


class IsAdminType(permissions.BasePermission):
    def has_permission(self, request, view):
        return is_admin_user(request.user)


class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return is_admin_user(request.user)


class IsAdminOrCompanyType(permissions.BasePermission):
    def has_permission(self, request, view):
        return is_admin_user(request.user) or is_company_user(request.user)
