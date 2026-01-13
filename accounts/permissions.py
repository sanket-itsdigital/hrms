"""
Custom permissions for accounts app.
"""
from rest_framework import permissions


class IsCEO(permissions.BasePermission):
    """
    Permission class to check if user is CEO.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_ceo


class IsHR(permissions.BasePermission):
    """
    Permission class to check if user is HR.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_hr


class IsPM(permissions.BasePermission):
    """
    Permission class to check if user is Project Manager.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_pm


class IsCEOOrHR(permissions.BasePermission):
    """
    Permission class to check if user is CEO or HR.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and (request.user.is_ceo or request.user.is_hr)


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Permission class to allow owners to edit, others to read.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user == request.user or request.user.is_ceo
