from rest_framework import permissions


class IsJournalist(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.groups.filter(name='Journalist').exists()


class IsEditor(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.groups.filter(name='Editor').exists()


class IsReader(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.groups.filter(name='Reader').exists()
