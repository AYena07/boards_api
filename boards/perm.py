from rest_framework import permissions
from django.contrib.auth.models import User


class IsOwnerOrBoardUser(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """
    def has_object_permission(self, request, view, obj):
        if (request.method in permissions.SAFE_METHODS or request.method == 'POST') and request.user in obj.users.all():
            return True
        return obj.owner == request.user


class IsSectionUser(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.board.owner == request.user or request.user in obj.board.users.all()


class IsStickerUser(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.section.board.owner == request.user or request.user in obj.section.board.users.all()


class IsAdminOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS and request.method != 'POST':
            return True
        return request.user.is_superuser
