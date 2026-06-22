from rest_framework import permissions


class IsJournalist(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.groups.filter(name='Journalist').exists()


class IsEditor(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.groups.filter(name='Editor').exists()


class IsEditorOrJournalist(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return (
            request.user.groups.filter(name='Editor').exists() or
            request.user.groups.filter(name='Journalist').exists()
        )
