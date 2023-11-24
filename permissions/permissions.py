from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsAdminOrIfAuthenticatedReadOnly(BasePermission):
    def has_permission(self, request, view):
        return bool(
            (
                    request.method in SAFE_METHODS
                    and request.user
                    and request.user.is_authenticated
            )
            or (request.user and request.user.is_staff)
        )


class IsAdminOrOwner(BasePermission):
    def has_object_permission(self, request, view, obj) -> bool:
        return obj.borrowing.user == request.user or request.user.is_staff
